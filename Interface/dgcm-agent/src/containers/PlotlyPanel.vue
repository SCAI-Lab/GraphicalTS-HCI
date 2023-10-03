<template>
  <div>
    <div class="flex-container">
      <el-input-number v-model="simLength" :min="0"></el-input-number>
      <el-button class="simple-button" @click="getDataAndPlot">Simulate</el-button>
    </div>
    <div id="simOutput">
      <div ref="plotlyChart"></div>
    </div>
  </div>
</template>

<script>
import Plotly from "plotly.js/dist/plotly"
import apiClient from '@/axiosConfig.js';

export default {
  data() {
    return {
      simLength: 0,
      chartData: null,
      chartLayout: null
    }
  },
  methods: {
    getDataAndPlot() {
      const requestData = {
        len: Math.floor(this.simLength)
      };
      apiClient.post('/plotly', requestData)
      .then(response => {
        this.chartData = response.data.data;
        this.chartLayout = response.data.layout;
        Plotly.newPlot(this.$refs.plotlyChart, this.chartData, this.chartLayout)
      })
      .catch(error => {
        console.error('Error:', error);
      });
    }
  }
}
</script>

<style scoped>
.flex-container {
  display: flex;
  align-items: center; 
  justify-content: flex-start; 
  gap: 1rem; 
}
</style>