<template>
<b-navbar toggleable="lg" type="dark" variant="info">
  <b-navbar-brand href="/">Webcrate</b-navbar-brand>
  <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>
  <b-collapse id="nav-collapse" is-nav>
    <b-navbar-nav>
      <b-nav-item href="/admin/projects">Projects</b-nav-item>
    </b-navbar-nav>
    <b-navbar-nav class="ml-auto">
      <b-nav-item-dropdown right>
        <template v-slot:button-content><em>{{ user }}</em></template>
        <b-dropdown-item href="/logout">Log Out</b-dropdown-item>
      </b-nav-item-dropdown>
    </b-navbar-nav>
  </b-collapse>
</b-navbar>
</template>

<script>

import { mapState } from 'vuex'

export default {

  computed: {

    localComputed () {

    },

    ...mapState({

      user: state => state.user,
      actual: state => state.actual

    })

  }

}

</script>
