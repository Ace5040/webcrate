<template>
<div class="login-page">
  <b-navbar toggleable="lg" type="dark" variant="info">
    <b-navbar-brand href="/">Webcrate</b-navbar-brand>
    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>
  </b-navbar>
  <div v-if="error" v-html="error_message" class="text-center alert alert-danger"></div>
  <b-container>
    <b-form class="login-form" method="post">
      <h1>Please Sign In</h1>
      <b-form-group id="email" label="Email address:" label-for="email">
      <b-form-input
        id="email"
        name="email"
        v-model="last_username"
        type="email"
        required
        placeholder="Enter email"
      ></b-form-input>
      </b-form-group>
      <b-form-group id="password" label="Password:" label-for="password">
      <b-form-input
        id="password"
        name="password"
        type="password"
        required
        placeholder="Enter password"
      ></b-form-input>
      </b-form-group>
      <input name="_csrf_token" v-model="csrf_token" type="hidden"/>
      <b-button type="submit" variant="primary">Sign in</b-button>
    </b-form>
  </b-container>
</div>
</template>

<script>

export default {

  created () {

  },

  components: {
  },

  data: () => ({
    error: error,
    error_message: error_message,
    csrf_token: csrf_token,
    last_username: last_username
  }),

  computed: {

  },

  watch: {

  },

  mounted () {

  },

  methods: {


  }


}

</script>

<style scoped>

.login-form {
    max-width: 350px;
    margin: 20px auto 0;
}

</style>
