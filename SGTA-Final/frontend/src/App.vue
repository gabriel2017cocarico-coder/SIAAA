<template>
  <RouterView />
  <FirmaDialogo />
  <BotonTutorialRol />
  <AsistenteChat />
</template>

<script setup>
import { RouterView } from 'vue-router'
import FirmaDialogo from './components/FirmaDialogo.vue'
import BotonTutorialRol from './components/BotonTutorialRol.vue'
import AsistenteChat from './components/AsistenteChat.vue'
</script>

<style>
html,
body,
#app {
  margin: 0;
  width: 100%;
  min-width: 320px;
  min-height: 100%;
}

body {
  min-height: 100vh;
}
</style>
