<template>
    <div ref="networkContainer" id="network-container">
    </div>

    <el-dialog v-model="isEdgeEditing" @close="handleEdgeCancel" :show-close="false" width="40%">
      <template #header="{ close, titleId, titleClass }">
        <div class="my-header">
          <h2 :id="titleId" :class="titleClass">Edit Edge from <i>"{{ currentU }}"</i> to <i>"{{ currentV }}"</i></h2>
          <el-button type="danger" @click="close">
            <el-icon class="el-icon--left"><CircleCloseFilled /></el-icon>
            Close
          </el-button>
        </div>
      </template>
      <EdgeEditor 
        ref="edgeEditor"
        @save-edge="handleEdgeSave" 
        @cancel-edge="handleEdgeCancel"
      />
    </el-dialog>

    <el-dialog v-model="isNodeEditing" @close="handleNodeCancel" :show-close="false" width="40%">
      <template #header="{ close, titleId, titleClass }">
        <div class="my-header">
          <h2 :id="titleId" :class="titleClass">Edit Node</h2>
          <el-button type="danger" @click="close">
            <el-icon class="el-icon--left"><CircleCloseFilled /></el-icon>
            Close
          </el-button>
        </div>
      </template>
      <NodeEditor
      ref="nodeEditor"
      @save-node="handleNodeSave"
      @cancel-node="handleNodeCancel"
      />
    </el-dialog>

</template>
  
<script>
import { toRaw } from 'vue';
import { Network, DataSet, DataView } from "vis-network/standalone/umd/vis-network";





import apiClient from '@/axiosConfig.js';

import EdgeEditor from './EdgeEditor.vue';
import NodeEditor from './NodeEditor.vue';

export default {
  props: ['graph', 'edgesFilterValues', 'currentEdited'],
  emits: ['edge-added', 'node-added'],
  components: {
    EdgeEditor,
    NodeEditor
  },
  data() {
    return {
      network: null,
      edgesview: null,
      isEdgeEditing: false,  // for toggling popup
      isNodeEditing: false,  // for toggling popup
      
      last: {
        callback: null
      },

      currentU: '',
      currentV: '',
    }
  },


  methods: {

    renderGraph() {
      const graph = toRaw(this.graph);
      const nodes = new DataSet(graph.nodes);
      const edges = new DataSet(graph.edges);

      // configure edge filter
      const edgesFilter = (edge) => {
        return this.edgesFilterValues[edge.lag];
        // select edges based on current selection mode
        // modes: ['todo', 'lag', 'expert', 'machine']
      };
      this.edgesView = new DataView(edges, { filter: edgesFilter });

      // chunck all the information
      const options = {
        interaction: { hover: true },
        manipulation: {
          enabled: true,

          addNode: this.addNodePL,
          editNode: this.editNodePL,

          addEdge: this.addEdgePL,
          editEdge: {
              editWithoutDrag: this.editEdgePL,
          },

          deleteEdge: this.deleteEdgePL
          
        },
      };
      
      this.network = new Network(this.$refs.networkContainer, { nodes: nodes, edges: this.edgesView }, options);

      // set event listener 
    },

    handleFilterChange() {
      this.edgesView.refresh();
    },

    // #################################
    // #region NODE
    addNodePL(visNodeData, callback) {
      visNodeData.id=undefined; // dirty for vis-network
      this._popNodeDialog('add', visNodeData);

      this.last.callback = callback;
    },

    editNodePL(visNodeData, callback) {
      this._postNodeAttr(visNodeData.id).then(attr => {
        this._popNodeDialog('edit', {
          ...attr,
          ...visNodeData, // type is duplicated 
        });
        this.last.callback = callback; 
      });
    },

    handleNodeSave(usrNodeData) {
      // additionalNodeInfo { edit_type, data }
      this._hideNodeDialog();
      this._postNodeChange(usrNodeData).then(visNodeData => {
        // data { id, title, color, ... }
        this._announceNodeUpward(visNodeData, usrNodeData.edit_type);
        console.log(visNodeData);
        if (usrNodeData.edit_type === 'add') {
          this.network.body.data.nodes.getDataSet().add(visNodeData);
        }
        if (usrNodeData.edit_type === 'edit') {
          this.network.body.data.nodes.getDataSet().update(visNodeData);
        }
        
      });
    },

    handleNodeCancel() {
      this.isNodeEditing = false;
      if (this.last.callback !== null) {
        this.last.callback(null);
      }

    },
    // #endregion
    // #################################

    // #################################
    // #region EDGE
    addEdgePL(visEdgeData, callback) {
      this.currentU = visEdgeData.from;
      this.currentV = visEdgeData.to;

      this._popEdgeDialog('add', visEdgeData);
      this.last.callback = callback; 
    },

    editEdgePL(visEdgeData, callback) {
      this.currentU = visEdgeData.from;
      this.currentV = visEdgeData.to;

      const eid = visEdgeData.id;

      const lag = this.network.body.data.edges.getDataSet().get(eid).lag;
      this._postEdgeAttr(eid).then(attr => {
        this._popEdgeDialog('edit', {
          ...attr,
          ...visEdgeData,
          lag: lag
        });
        
        this.last.callback = callback; 
      });
    },

    deleteEdgePL(visEdgeData, callback) {
      console.log(visEdgeData);
      console.log(callback);
      callback(visEdgeData);
    },

    handleEdgeSave(usrEdgeData) {
      // addtionalEdgeInfo  {edit_type: this.edit_type, data:userData} . 
      this._hideEdgeDialog();

      this._postEdgeChange(usrEdgeData).then(visEdgeData => {
        // data { from, to, lag, title, color, arrows }
        this._announceEdgeUpward(visEdgeData, usrEdgeData.edit_type);
        if (usrEdgeData.edit_type === 'add') {
          this.network.body.data.edges.getDataSet().add(visEdgeData);
        }
        if (usrEdgeData.edit_type === 'edit') {
          this.network.body.data.edges.getDataSet().update(visEdgeData);
        }
      });
      
    },
    
    handleEdgeCancel() {
      this._hideEdgeDialog();
      if (this.last.callback !== null) {
        this.last.callback(null);
        this.last.callback = null;
      }
    },

    handleEdgeDeletion(eid) {
      console.log(eid);
      
    },
    // #endregion EDGE
    // #################################


    // #################################
    // #region backend 
    async _postEdgeChange(usrEdgeData) {
      const edgeInfo = usrEdgeData.data;
      const edit_type = usrEdgeData.edit_type;
      // edge info { from: to: lag: attr: }
      try {
        var response = null;
        if (edit_type === "add") {
          response = await apiClient.post('/edit/add_edge', edgeInfo);
        }
        if (edit_type === "edit") {
          response = await apiClient.post('/edit/update_edge', edgeInfo);
        }
        return response.data;
        // If axios call succeeds, call the callback
      } catch (error) {
        console.error('Error posting data:', error);
        // Handle the error accordingly
      }

    },

    async _postNodeChange(usrNodeData) {
      const nodeInfo = usrNodeData.data;
      const edit_type = usrNodeData.edit_type;
      // node info { nodeName: , attr:, }
      try {
        var response = null;
        if (edit_type === "add") {
          response = await apiClient.post('/edit/add_node', nodeInfo);
        }
        if (edit_type === "edit") {
          response = await apiClient.post('/edit/update_node', nodeInfo);
        }
        return response.data;
        // If axios call succeeds, call the callback
      } catch (error) {
        console.error('Error posting data:', error);
        // Handle the error accordingly
      }
    },

    async _postEdgeAttr(edgeID) {
      try {
        const response = await apiClient.post('/query/get_edge', {eid: edgeID});
        return response.data
      } catch (error) {
        console.error('Error posting data:', error);
        // Handle the error accordingly
        return null;
      }
    },

    async _postNodeAttr(nodeID) {
      try {
        const response = await apiClient.post('/query/get_node', {nodeName: nodeID});
        return response.data
      } catch (error) {
        console.error('Error posting data:', error);
        return null;
      }
    },

    async _popEdgeDialog(editMode, edgeData) {

      this.isEdgeEditing = true;

      const uType = this._getTypeforNode(edgeData.from);
      const vType = this._getTypeforNode(edgeData.to);

      const promises = [];

      if (uType === 'categorical') {
        promises.push(
          this._postNodeAttr(edgeData.from).then(dbNodeAttrU => {
            edgeData.uValEncode = dbNodeAttrU.val_encode;
          })
        );
      }

      if (uType === 'continuous') {
        promises.push(
          this._postNodeAttr(edgeData.from).then(dbNodeAttrU => {
            edgeData.uRange = dbNodeAttrU.range;
          })
        );
      }

      if (vType === 'categorical') {
        console.log("here!")
        promises.push(
          this._postNodeAttr(edgeData.to).then(dbNodeAttrV => {
            edgeData.vValEncode = dbNodeAttrV.val_encode;
          })
        );
      }

      // Wait for all promises to resolve
      await Promise.all(promises);

      this.$nextTick(() => {
        console.log(edgeData)
        this.$refs.edgeEditor.setData(uType, vType, edgeData);
        this.$refs.edgeEditor.setEditMode(editMode);
      });

    },
    
    _getTypeforNode(NodeID) {
      return this.network.body.data.nodes.getDataSet().get(NodeID).type;
    },

    _hideEdgeDialog() {
      this.isEdgeEditing = false;
    },

    _popNodeDialog(editMode, dbNodeData) {
      this.isNodeEditing = true;

      this.$nextTick(() => {      
        this.$refs.nodeEditor.setData(dbNodeData);
        this.$refs.nodeEditor.setEditMode(editMode);
      });
    },

    _hideNodeDialog() {
      this.isNodeEditing = false;
    },

    _announceEdgeUpward(visEdgeData, edit_type) { 
      if (edit_type === 'add') {
           this.$emit('edge-added', visEdgeData);
        }
        if (edit_type === 'edit') {
          this.$emit('edge-updated', visEdgeData);
        }
    },

    _announceNodeUpward(visNodeData, edit_type) { 
      if (edit_type === 'add') {
           this.$emit('node-added', visNodeData);
        }
        if (edit_type === 'edit') {
          this.$emit('node-updated', visNodeData);
        }
    },

    // #endregion
    // #################################
    
    // #################################
    // #region dirty


      // #endregion
    // #################################
  }
}
</script>
  

<style>
#network-container {
  height: 500px;
  border: 1px solid lightgray;
  border-radius: 20px;
}

.my-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.el-dialog__body {
    padding-top: 0px;
}

</style>