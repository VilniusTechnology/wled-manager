<template>
  <span class="loading-dots">...</span>
</template>

<style scoped>
@keyframes loadingDots {
  0% { content: '.'; }
  33% { content: '..'; }
  66% { content: '...'; }
  100% { content: ''; }
}

.loading-dots {
  position: relative;
}

.loading-dots::after {
  content: '';
  animation: loadingDots 1.5s infinite steps(1);
  display: inline-block;
  width: 1em;
}
</style>