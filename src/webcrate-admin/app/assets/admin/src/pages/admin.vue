<template>
<div class="admin-page">
  <b-list-group>
    <b-list-group-item v-for="item in soft" v-bind:key="item.name" class="d-flex justify-content-between align-items-center">
      {{ item.name }}
      <b-badge variant="primary" pill>{{ item.version ? item.version : 'n/a' }}</b-badge>
    </b-list-group-item>
  </b-list-group>
</div>
</template>

<script>

export default {

  data: () => ({
    soft: soft
  })

}

</script>
