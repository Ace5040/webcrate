<template>
<svg :width="size" :height="size" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Top face -->
  <path d="M14 2 L26 8 L14 14 L2 8 Z"
    fill="rgba(255,255,255,0.42)"
    stroke="rgba(255,255,255,0.95)"
    stroke-width="1.2"
    stroke-linejoin="round"
  />
  <!-- Left face -->
  <path d="M2 8 L14 14 L14 26 L2 20 Z"
    fill="rgba(255,255,255,0.12)"
    stroke="rgba(255,255,255,0.95)"
    stroke-width="1.2"
    stroke-linejoin="round"
  />
  <!-- Right face -->
  <path d="M14 14 L26 8 L26 20 L14 26 Z"
    fill="rgba(255,255,255,0.26)"
    stroke="rgba(255,255,255,0.95)"
    stroke-width="1.2"
    stroke-linejoin="round"
  />
  <!-- Inner grid — top face -->
  <line x1="10" y1="5" x2="22" y2="11" stroke="rgba(255,255,255,0.3)" stroke-width="0.8"/>
  <line x1="18" y1="5" x2="26" y2="9" stroke="rgba(255,255,255,0.3)" stroke-width="0.8"/>
  <!-- Inner grid — right face -->
  <line x1="26" y1="12" x2="14" y2="18" stroke="rgba(255,255,255,0.2)" stroke-width="0.8"/>
  <line x1="26" y1="16" x2="14" y2="22" stroke="rgba(255,255,255,0.2)" stroke-width="0.8"/>
</svg>
</template>

<script setup>
defineProps({
  size: {
    type: Number,
    default: 28,
  },
})
</script>
