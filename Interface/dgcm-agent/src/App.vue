<template>
    <div id="app">
      <div id="parent-container">
        
        <div>
          <label>Filter Lags</label>
            <div id="lag-checkboxes">
              <div v-if="lags">
                <LagCheckbox 
                  v-for="(lag, index) in lags" 
                  :key="index" 
                  :lag="lag" 
                  :color="colors[lag]" 
                  :initialChecked="edgesFilterValues[lag]" 
                  @checkbox-changed="updateFilterValues"
                />
            </div>
          </div>
          <vs-checkbox v-model="all_checked"  @change="toggleAll(true)">all</vs-checkbox>
          <vs-checkbox v-model="none_checked" @change="toggleAll(false)">none</vs-checkbox>
        </div>

        <div id="network-container">
          <NetworkView :graph="graph" 
                       :edgesFilterValues="edgesFilterValues" 
                       ref="networkView" 
                       @edge-added="handleNewEdge"
                       @node-added="handleNewNode"
                       />
          
          <div id="control-panel">
            <vs-row vs-justify="space-between">
              <RenderSelection ref="renderSelection"
                            @update-graph-info="handleGraphUpdate"/>
              <vs-button color="danger" :disabled="!currentEdited">Export Current Graph</vs-button>
          </vs-row>
          </div>
        </div>
        <vs-button color="danger">Show Perturbation</vs-button>

      </div>

      <div id="plotly-container">
        <PlotlyPanel :plotData="plotData" />
      </div>

      <!-- <EdgeEditor :graph="graph" />
      <NodeEditor :graph="graph" /> -->
      
    </div>
</template>
  
<script>
  import NetworkView from './containers/NetworkView.vue'
  import PlotlyPanel from './containers/PlotlyPanel.vue'
  import RenderSelection from './containers/RenderSelection.vue'
  import LagCheckbox from './components/LagCheckbox.vue'

  
  export default {
    name: 'App',
    components: {
      NetworkView,
      LagCheckbox,
      PlotlyPanel,
      // EdgeEditor,
      // NodeEditor,
      RenderSelection,
    },
    data() {
      return {
        graph: {},
        lags : [],
        colors: {},
        plotData: {},
        edgesFilterValues: {},
        currentEdited: false,


        all_checked : false,
        
        none_checked : false
      }
    },


    watch : {
      check_num(newVal) {
        this.all_checked = (newVal === Object.keys(this.edgesFilterValues).length);
        this.none_checked = (newVal === 0)
      }
    },

    computed: {
      check_num() {
        return Object.values(this.edgesFilterValues).filter(Boolean).length
      }
    },

    methods: {
      // event handlers from children 

      // from render selection
      handleGraphUpdate(data) {
        this.graph = data.graph;
        this.lags = data.lags;
        this.colors = data.colors;
        this.edgesFilterValues = this.lags.reduce((obj, item) => {
          obj[item] = true;
          return obj;
        }, {});
        this.$nextTick(() => {
            this.$refs.networkView.renderGraph();
        });
      },

      // from network view
      handleNewEdge(newEdgeData) {
        this.currentEdited = true;
        if (!this.lags.includes(newEdgeData.lag)) {
          // Add the new lag to the lags array
          this.lags.push(newEdgeData.lag);
          this.lags.sort((a, b) => a - b);
          // Add corresponding data to other structures
          this.colors[newEdgeData.lag] = newEdgeData.color.color/* specify the new color */;
          this.edgesFilterValues[newEdgeData.lag] = true;

        } 
      },


      handleNewNode() {
        this.currentEdited = true;
      },


      // from check boxes
      updateFilterValues(data) {
        this.edgesFilterValues[data.lag] = data.checkState;
        this.$refs.networkView.handleFilterChange();
      },

      toggleAll(isSelected) {
        if (isSelected && !this.all_checked) {
          this.lags.forEach(lag => {
            this.edgesFilterValues[lag] = true;
          });
        }
        if (!isSelected && !this.none_checked) {
          this.lags.forEach(lag => {
            this.edgesFilterValues[lag] = false;
          });
        }
        
      },

    }
  };
</script>
  

<style scoped>
#app {
  font-family:'Courier New', Courier, monospace;
  justify-content: center;
  padding: 20px;
}
#parent-container {
  display: flex;
  align-items: start; /* Align children to the start of the container vertically */
  gap: 20px; /* Gap between children */      
  padding: 20px;
}
#network-container {
  width: 80%;
  aspect-ratio: 1/1;
  border: 1px solid #ddd; /* For visualization */
  margin-bottom: 20px; /* Gap between components */
  box-sizing: border-box; /* To include padding and border in element's total width and height */
  border-radius: 20px;
}

#checkbox-panel {
  display: flex;
  flex-direction: column;
  justify-items: center;
  width: 120px;
  min-height: 50px; /* Adjust based on your preference */
  border: 1px solid #ddd; /* For visualization */
  margin-bottom: 20px; /* Gap between components */
  box-sizing: border-box; /* To include padding and border in element's total width and height */

}

#plotly-container {
  width: 100%;
  height: 500px; /* Adjust based on your preference */
  border: 1px solid #ddd; /* For visualization */
  border-radius: 20px;
  padding: 20px;
  margin-top: 20px;
}


#checkbox-container {
  display: flex;
  flex-direction: row;
  justify-content: center;
  width: 120px;
  min-height: 50px; /* Adjust based on your preference */
  margin-bottom: 20px; /* Gap between components */
  box-sizing: border-box; /* To include padding and border in element's total width and height */

}

#control-panel {
  padding-left: 20px;
  padding-top: 10px;
  padding-bottom: 10px;
}
#lag-checkboxes {
  border: 1px solid #ddd; /* For visualization */
  border-radius: 10px;
}

</style>


<style>
.simple-button {
    padding: 6px 10px;
    background-color: #469fff;
    color: white;
    border: none;
    cursor: pointer;
    margin: 3px;
    border-radius: 5px;
}

.vs-checkbox {
    height: 10px;
    width: 10px;
}
.vs-checkbox-primary {
  justify-content: left;
}

</style>