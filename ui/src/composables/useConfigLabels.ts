import { configLabels } from '../i18n/config-labels'

export function useConfigLabels() {
    const getLabel = (path: string): string => {
        // 1. Direct match
        if (configLabels[path]) {
            return configLabels[path]
        }

        // 2. Handle array indices (e.g., seg[0].col -> seg.col)
        // Replace [number] with nothing to find the base key
        // But we might want to preserve the context for the label

        // Example: "seg[0].col" -> match against "seg.col"
        const genericPath = path.replace(/\[\d+\]/g, '')
        if (configLabels[genericPath]) {
            const label = configLabels[genericPath]

            // If it's a segment, try to make it more descriptive
            if (path.startsWith('seg[')) {
                const segMatch = path.match(/seg\[(\d+)\]/)
                if (segMatch) {
                    const index = parseInt(segMatch[1]) + 1 // 1-based index for humans
                    // If the path is exact match for segment object
                    if (genericPath === 'seg') {
                        return `Segment ${index}`
                    }
                    // If it's a property of a segment
                    return `${label} (Segment ${index})`
                }
            }

            // Generic array handling
            const arrayMatch = path.match(/\[(\d+)\]/)
            if (arrayMatch) {
                const index = parseInt(arrayMatch[1]) + 1
                return `${label} #${index}`
            }

            return label
        }

        // 3. Last fallback: return the full path as requested
        // This ensures context is preserved for deep objects (e.g. network.wifi.ip)
        return path
    }

    return {
        getLabel
    }
}
