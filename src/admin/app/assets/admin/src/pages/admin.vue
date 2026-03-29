<template>
<div class="admin-page">
  <ul class="list-group">
    <li
      v-for="item in soft"
      :key="item.name"
      class="list-group-item d-flex justify-content-between align-items-center"
    >
      {{ item.name }}
      <span class="badge text-bg-primary rounded-pill">{{ item.version ? item.version : 'n/a' }}</span>
    </li>
  </ul>
</div>
</template>

<script setup>
const soft = window.soft || []
</script>
