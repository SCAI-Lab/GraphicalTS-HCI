<template>
    <div>

    <div class="row-container">
        <div class="left-group">
            <div>
                <el-select placeholder="Please select a graph" v-model="selectedGraph">
                    <el-option :key="graph" :value="graph" v-for="graph in graphs" />
                    
                </el-select>
            </div>
            <div>
                <el-button style="width:120px" :disabled="selectedGraph===''" @click="sendGraphToModerator">Render Selected</el-button>
            </div>
            <div>
                <el-button style="width:120px" @click="isUploading=true">Upload New</el-button>
            </div>
        </div>
    </div>

        
        
     </div>
    <el-dialog title="Upload a new Graph" v-model:active="isUploading"><UploadZip @new-uploaded="handleNewUploadedGraph"/></el-dialog>
  </template>

<script>
import UploadZip from './render_selection/UploadZip.vue'

import apiClient from '@/axiosConfig.js';

export default {
    components: {
        UploadZip
    },
    data() {
        return {
            graphs: [],
            selectedGraph: '',
            isUploading: false
        }
    },
    
    created() {
        this.fetchGraphs();
    },

    methods: {     
        async fetchGraphs() {
            try {
                const response = await apiClient.post("/all_graphs");
                this.graphs = response.data;
                } 
            catch (error) {
                console.error("Error fetching graphs:", error);
            }
        },  
        
        
        sendGraphToModerator() {
            apiClient.post('/load_graph', { graph_name: this.selectedGraph })
            .then(response => {
                const datapackage = response.data;
                this.$emit('update-graph-info', datapackage);
            })
            .catch(error => {
                console.error("Error fetching datapackage:", error);
            });
        },
        
        handleNewUploadedGraph(graph_name) {
            this.graphs.push(graph_name);
            this.selectedGraph = graph_name;
        },

        selectGraph(graph) {
            this.selectedGraph = graph;
        }
    }
    
}

</script>

<style>
.row-container {
    display: flex;
    justify-content: space-between;
}
.left-group {
    display: flex;
}
.left-group > div:not(:last-child) {
    margin-right: 20px;  /* Adjust for desired space between divs */
}

</style>