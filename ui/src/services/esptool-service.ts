import { ESPLoader, Transport } from 'esptool-js'
import type { IEspLoaderTerminal } from 'esptool-js'

export interface ChipInfo {
  chipName: string
  macAddress: string
  features: string[]
  flashSize?: string
}

export interface FlashProgress {
  percentage: number
  writtenBytes: number
  totalBytes: number
  currentPhase: 'erasing' | 'writing' | 'verifying' | 'done' | 'error'
  statusText: string
}

export class WebSerialService {
  private port: any = null
  private transport: Transport | null = null
  private esploader: ESPLoader | null = null
  private reader: ReadableStreamDefaultReader<string> | null = null
  private writer: WritableStreamDefaultWriter<string> | null = null
  private isTerminalActive: boolean = false
  private logCallback?: (log: string) => void
  private chipInfo: ChipInfo | null = null

  public isSupported(): boolean {
    return typeof navigator !== 'undefined' && 'serial' in navigator
  }

  public hasPort(): boolean {
    return this.port !== null
  }

  public setLogger(callback: (log: string) => void) {
    this.logCallback = callback
  }

  private log(message: string) {
    if (this.logCallback) {
      this.logCallback(message)
    }
  }

  public async requestPort(): Promise<boolean> {
    if (!this.isSupported()) {
      throw new Error('WebSerial API is not supported in this browser. Please use Chrome, Edge, or Opera.')
    }

    try {
      this.port = await (navigator as any).serial.requestPort()
      return true
    } catch (err: any) {
      if (err.name === 'NotFoundError') {
        this.log('User cancelled port selection.')
        return false
      }
      throw err
    }
  }

  public async connectAndDetect(baudRate: number = 115200): Promise<ChipInfo> {
    if (!this.port) {
      throw new Error('No serial port selected. Call requestPort() first.')
    }

    this.log(`Connecting to serial port at ${baudRate} baud...`)
    this.transport = new Transport(this.port, true)

    const terminalWrapper: IEspLoaderTerminal = {
      clean: () => {},
      writeLine: (data: string) => this.log(data),
      write: (data: string) => this.log(data)
    }

    this.esploader = new ESPLoader({
      transport: this.transport,
      baudrate: baudRate,
      terminal: terminalWrapper,
      debugLogging: false
    })

    this.log('Syncing with ESP bootloader...')
    const chip = await this.esploader.main()
    this.log(`Detected chip: ${chip}`)

    // Read flash size if available
    let flashSizeStr = 'Unknown'
    try {
      flashSizeStr = await this.esploader.detectFlashSize()
    } catch {
      // ignore
    }

    this.chipInfo = {
      chipName: chip || 'ESP Device',
      macAddress: 'Detected',
      features: [],
      flashSize: flashSizeStr
    }

    this.log(`Connected! Chip: ${this.chipInfo.chipName}, Flash: ${this.chipInfo.flashSize}`)
    return this.chipInfo
  }

  public async flashFirmware(
    binaryData: Uint8Array | ArrayBuffer,
    flashOffset: number = 0x0000,
    eraseAll: boolean = false,
    onProgress?: (progress: FlashProgress) => void
  ): Promise<void> {
    if (!this.esploader) {
      throw new Error('ESP Loader not initialized. Connect to device first.')
    }

    const dataArray = binaryData instanceof Uint8Array ? binaryData : new Uint8Array(binaryData)
    const totalBytes = dataArray.byteLength

    this.log(`Preparing to flash ${totalBytes} bytes at offset 0x${flashOffset.toString(16)}...`)

    if (onProgress) {
      onProgress({
        percentage: 0,
        writtenBytes: 0,
        totalBytes,
        currentPhase: eraseAll ? 'erasing' : 'writing',
        statusText: eraseAll ? 'Erasing flash memory...' : 'Starting firmware flash...'
      })
    }

    const fileArray = [
      {
        data: dataArray,
        address: flashOffset
      }
    ]

    await this.esploader.writeFlash({
      fileArray: fileArray,
      flashMode: 'keep',
      flashFreq: 'keep',
      flashSize: 'keep',
      eraseAll: eraseAll,
      compress: true,
      reportProgress: (_fileIndex: number, written: number, total: number) => {
        const pct = Math.min(100, Math.round((written / total) * 100))
        if (onProgress) {
          onProgress({
            percentage: pct,
            writtenBytes: written,
            totalBytes: total,
            currentPhase: pct < 100 ? 'writing' : 'verifying',
            statusText: pct < 100 ? `Writing flash: ${pct}%` : 'Verifying written data...'
          })
        }
      }
    })

    this.log('Flashing completed successfully!')
    if (onProgress) {
      onProgress({
        percentage: 100,
        writtenBytes: totalBytes,
        totalBytes,
        currentPhase: 'done',
        statusText: 'Flashing completed successfully!'
      })
    }

    // Reset device to boot into Tasmota
    try {
      this.log('Rebooting device into Tasmota...')
      await this.esploader.after('hard_reset')
    } catch (e) {
      this.log(`Reset notification: ${e}`)
    }
  }

  public async startSerialTerminal(
    baudRate: number = 115200,
    onDataReceived: (text: string) => void
  ): Promise<void> {
    this.log(`Opening serial terminal at ${baudRate} baud...`)

    // Disconnect ESPLoader transport if still open
    if (this.transport) {
      try {
        await this.transport.disconnect()
      } catch {
        // ignore
      }
      this.transport = null
      this.esploader = null
    }

    if (!this.port) {
      throw new Error('Port is not available.')
    }

    // Open port for raw streaming
    if (!this.port.readable || !this.port.writable) {
      await this.port.open({ baudRate: baudRate, dataBits: 8, stopBits: 1, parity: 'none' })
    }

    // Release ESP from reset state by clearing DTR and RTS
    try {
      await this.port.setSignals({ dataTerminalReady: false, requestToSend: false })
    } catch (e) {
      // Ignore if not supported on this platform
    }

    this.isTerminalActive = true

    // Start background reader loop
    const textDecoderStream = new TextDecoderStream()
    this.port.readable.pipeTo(textDecoderStream.writable).catch(() => {})
    this.reader = textDecoderStream.readable.getReader()

    const textEncoderStream = new TextEncoderStream()
    textEncoderStream.readable.pipeTo(this.port.writable).catch(() => {})
    this.writer = textEncoderStream.writable.getWriter()

    this.readTerminalLoop(onDataReceived)
  }

  private async readTerminalLoop(onDataReceived: (text: string) => void) {
    try {
      while (this.isTerminalActive && this.reader) {
        const { value, done } = await this.reader.read()
        if (done) break
        if (value) {
          onDataReceived(value)
        }
      }
    } catch (err: any) {
      if (this.isTerminalActive) {
        this.log(`Terminal read error: ${err.message || err}`)
      }
    }
  }

  public async sendSerialCommand(command: string): Promise<void> {
    if (!this.writer) {
      throw new Error('Serial terminal is not connected. Call startSerialTerminal() first.')
    }
    const cleanCmd = command.trim() + '\r\n'
    this.log(`> ${command.trim()}`)
    await this.writer.write(cleanCmd)
  }

  public async disconnect(): Promise<void> {
    this.isTerminalActive = false

    if (this.reader) {
      try {
        await this.reader.cancel()
        this.reader.releaseLock()
      } catch {
        // ignore
      }
      this.reader = null
    }

    if (this.writer) {
      try {
        await this.writer.close()
        this.writer.releaseLock()
      } catch {
        // ignore
      }
      this.writer = null
    }

    if (this.transport) {
      try {
        await this.transport.disconnect()
      } catch {
        // ignore
      }
      this.transport = null
      this.esploader = null
    }

    if (this.port) {
      try {
        await this.port.close()
      } catch {
        // ignore
      }
      this.port = null
    }

    this.chipInfo = null
    this.log('Disconnected from serial port.')
  }
}

export const webSerialService = new WebSerialService()
