<template>
  <!-- Use Suspense to load async component (Page) -->
  <RouterView v-slot="{ Component }">
    <template v-if="Component">
      <Transition mode="out-in">
        <KeepAlive>
          <Suspense>
            <component :is="Component"></component>
            <template #fallback>Loading app...</template>
          </Suspense>
        </KeepAlive>
      </Transition>
    </template>
  </RouterView>
</template>

<script setup>
import { provide } from "vue";
const baseURL = "http://localhost:3008"; // local development
provide("baseURL", { baseURL });
</script>

<style lang="scss">
svg,
canvas {
  width: 100%;
  height: 100%;
}
</style>
