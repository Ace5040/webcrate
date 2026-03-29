<template>
<div class="login-page">
  <nav class="navbar navbar-expand-lg navbar-dark bg-info">
    <div class="container-fluid">
      <a class="navbar-brand" href="/">Webcrate</a>
    </div>
  </nav>
  <div v-if="error" v-html="errorMessage" class="text-center alert alert-danger"></div>
  <div class="container">
    <form class="login-form" method="post">
      <h1>Please Sign In</h1>
      <div class="mb-3">
        <label for="email" class="form-label">Email address:</label>
        <input
          id="email"
          v-model="lastUsername"
          name="email"
          type="email"
          required
          placeholder="Enter email"
          class="form-control"
        >
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password:</label>
        <input
          id="password"
          name="password"
          type="password"
          required
          placeholder="Enter password"
          class="form-control"
        >
      </div>
      <input name="_csrf_token" :value="csrfToken" type="hidden">
      <button type="submit" class="btn btn-primary">Sign in</button>
    </form>
  </div>
</div>
</template>

<script setup>
import { ref } from 'vue'

const error = ref(window.error)
const errorMessage = ref(window.error_message)
const csrfToken = ref(window.csrf_token)
const lastUsername = ref(window.last_username)
</script>

<style scoped>
.login-form {
    max-width: 350px;
    margin: 20px auto 0;
}
</style>
