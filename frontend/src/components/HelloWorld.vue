<template>
  <v-container>
    <v-row>
      <v-col v-for="n in 3" :key="n">
        <v-btn>some TITLE</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang='ts'>
import { defineComponent } from 'vue'


export default defineComponent({
  name: 'HelloWorld',
})
</script>
