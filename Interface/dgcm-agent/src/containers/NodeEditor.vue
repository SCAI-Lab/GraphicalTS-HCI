<template>
  <div>
      <div class="node-options">
          <div class="basic-tools">
            <h3>Basic Infomation</h3>
            <el-row style="justify-items: center;">
                  <el-col :span="5"><el-text>Node Name:</el-text></el-col>
                  <el-col :span="8">
                    <el-input 
                    placeholder="Placeholder" 
                    v-model="nodeName" :disabled="edit_type==='edit'" 
                    @input="() => { this.alertShow=(this.nodeName==='');
                                    this.alertMsg='Node name cannot be empty';
                                  }"/>
                  </el-col>
            </el-row>
            <el-row>
              <el-col :span="5"><el-text>Node Type:</el-text></el-col>
                  <el-col :span="19">
                    <el-radio-group v-model="nodeType">
                      <el-radio label="continuous"/>
                      <el-radio label="categorical"/>
                      <el-radio label="binary"/>
                    </el-radio-group>
              </el-col>
            </el-row>

                  
                  <!-- <el-select v-model="nodeType" id="nodeType">
                      <el-option :key="item.key" :value="item.modelValue" :text="item.text" v-for="item in typeOptions"></el-option>
                  </el-select> -->
              
          </div>


          <div v-if="nodeType==='categorical'">
            <h3>For Categorical Variables: Add Possible Values</h3>
            
              <div class="category-tools">              
                <el-tag
                  :key="chip"
                  @close="_remove(chip)"
                  closable
                  class="mx-1"
                  :disable-transitions="false"
                  v-for="chip in valChips"
                  round
                  size="large"
                  >
                  {{ chip }}
                </el-tag>
                <div class="input-button-wrapper">
                  <div v-if="newItemInputVisible" class="tag-input">
                    <el-input 
                        ref="newItemInput" 
                        v-model="newItemInputValue" 
                        @keyup.enter="handleInputConfirm" 
                        @blur="handleInputBlur">
                    </el-input>
                    <el-button @click="handleInputConfirm"
                               size="small"
                               type="primary"
                               
                               :disabled="newItemInputValue===''"
                               style="position: absolute; right: 1px; margin: 2px; height: 24px; width:10px; align-self: center;">
                      <el-icon>
                        <Select/>
                      </el-icon>
                    </el-button>
                  </div>
                  <el-button v-else 
                    @click="showInput" 
                    style="width:100%"
                    round>
                    <el-icon><CirclePlusFilled/></el-icon>&nbsp; Value
                  </el-button>
                </div>

            </div>
          </div>

          
          <div v-if="nodeType==='continuous'">
                <h3>Range for continuous variable</h3>

                <div class="range-tools">            
                  <div class="flex-item">
                    <el-text size="small">Min</el-text>
                    <el-input-number v-model="valRange[0]" :max="valRange[1]"></el-input-number>
                  </div>

                  <div class="flex-item">
                      <el-text size="small">offset</el-text>
                      <el-input-number v-model="valOffset" :max="valRange[1]" :min="valRange[0]"></el-input-number>
                  </div>

                  <div class="flex-item">
                    <el-text size="small">Max</el-text>
                    <el-input-number v-model="valRange[1]" :min="valRange[0]"></el-input-number>
                  </div>
                </div>
          </div>

          <div class="common-end">
            <h3>Memo for this Node</h3>
            <el-input type="textarea"
                  id="memo" 
                  v-model="memo"
                  placeholder="(Optional) Further information about this node..."></el-input>

            <div class="control-tools">
              <el-button @click="save">Save</el-button>
              <el-button @click="cancel">Cancel</el-button>
            </div>
          </div>
          <div style="margin-top: 10px" v-show="alertShow">
            <el-alert title="Invalid Input" :description="alertMsg" type="error" show-icon  @close="() => { this.alertShow = false }"/>
          </div>
          


      </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
export default {
  data() {
    return {
      ...this.defaultNode(),
      edit_type: null,
      ...this.defaultOptions(),
      nodeFormData: this.defaultNode(),
    }
  },

  computed: {
    valEncode() {
      const newObject = {};
      // Helper function to get a unique integer
      const getUniqueInt = (usedValues) => {
          let i = 1;
          while (usedValues.has(i)) {
            i++;
          }
          return i;
      };
        // Set to store all values that have been used
      console.log(this.historicalEncode)
      const usedValues = new Set(Object.values(this.historicalEncode));

      this.valChips.forEach(str => {
        if (this.historicalEncode[str] !== undefined) {
          newObject[str] = this.historicalEncode[str];
        } else {
          const uniqueInt = getUniqueInt(usedValues);
          newObject[str] = uniqueInt;
          usedValues.add(uniqueInt);
        }
      });
      return newObject;
    }
  },




  methods: {
    defaultNode() {
      return {
        nodeName: '',
        memo: '',
        nodeType: '',
        is_todo: false,

        valRange: [0, 1], // continuous type  
        valOffset: 0,

        historicalEncode: {},
        valChips: []
        
      };
    },

    defaultOptions() {
      return {
        newItemInputVisible: false,
        newItemInputValue: '',
        alertShow: false,
        alertMsg: ''

      };
    },

    setData(dbNode) {
      const defaults = this.defaultNode();
      this.resetOptions();
      this._setEditorState(dbNode, defaults);
    },

    setEditMode(editMode) {
      this.edit_type = editMode;
    },

    save() {
      if (this.nodeType === '') {
        ElMessage({
          showClose: true,
          message: 'Node type cannot be empty',
          type: 'error',
        })
        return
      } 
      if (this.nodeName === '') {
        ElMessage({
          showClose: true,
          message: 'Node name cannot be empty',
          type: 'error',
        })
        return 
      }
      this.$emit('save-node', this._constructSavingData());
    },

    cancel() {

      this.$emit('cancel-node'); 
    },

    _setEditorState(dbNode, defaults) {
      this.nodeName = dbNode.id !== undefined ? dbNode.id : defaults.nodeName;
      
      this.nodeType = dbNode.type !== undefined ? dbNode.type : defaults.nodeType;
      this.memo = dbNode.memo !== undefined ? dbNode.memo : defaults.memo;
      this.is_todo = dbNode.is_todo !== undefined ? dbNode.is_todo: defaults.is_todo;

      this.valRange = dbNode.range !== undefined? dbNode.range: defaults.valRange;
      this.historicalEncode = dbNode.val_encode !== undefined ? dbNode.val_encode : defaults.historicalEncode;
      this.valChips = dbNode.val_encode !== undefined ? Object.keys(dbNode.val_encode): defaults.valChips;
      
    },

    _constructSavingData(){
      const baseInfo = {
        nodeName: this.nodeName,
      }
      // python style
      const attr = {
        is_todo: this.is_todo,
        memo: this.memo,
        type: this.nodeType,
      };

      if (this.nodeType === 'continuous') {
        attr.range = this.valRange;
        attr.offset = this.valOffset;
      }
      if (this.nodeType === 'categorical') {
        attr.val_encode = this.valEncode
      }
      
      return {
        edit_type: this.edit_type,
        data: {
          ...baseInfo,
          attr: attr,
        }
      }
    },

    _remove(item) {
      this.valChips.splice(this.valChips.indexOf(item), 1)
    },
    
    handleInputConfirm() {
      if (this.newItemInputValue) {
        if (!this.valChips.includes(this.newItemInputValue)) {
            this.valChips.push(this.newItemInputValue);
        } else {
          ElMessage({
            showClose: true,
            message: 'Duplicated Value',
            type: 'error',
          })
        }
      }
      // this.newItemInputVisible = false;
      this.newItemInputValue = '';
      this.$nextTick(() => {
        this.$refs.newItemInput.focus();
      })
    },

    handleInputBlur() {
      this.newItemInputValue = '';
      this.newItemInputVisible = false;

    },

    showInput() {
      this.newItemInputVisible = true;
      this.$nextTick(() => {
        this.$refs.newItemInput.focus();
      })
    },

    resetOptions() {
      const dopts = this.defaultOptions()
      Object.keys(dopts).forEach((key) => {
        this[key] = dopts[key];
      });
    },
  }
};
</script>

<style scoped>
.node-option {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: white;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border-radius: 5px;
}

.input-group {
  margin-bottom: 15px;
}

.input-button-wrapper {
    position: relative;
    /* Set a minimum height based on your requirements */
    min-height: 40px; 
}

.input-button-wrapper > * {
    position: absolute;
    top: 0;
    left: 0;
}

.range-tools{
    display: flex;
    align-items: center;
    justify-content: left;
}

.flex-item {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: left;
    margin: 10px;
}


.basic-tools {
    align-items: center;
    justify-content: left;
    flex-direction: column;
}

.basic-tools label {
    margin-bottom: 5px;
}

.basic-tools .input-container {
    width: 100%;
    flex-direction: column;
}
.category-tools {
  display: flex;
  flex-direction: row;
  border: 1px solid #9d9d9d;
  border-radius: 20px;
  align-items: center;
  padding-top: 5px;
  padding-right: 5px;
  padding-left: 5px;
  align-content: space-evenly;
  justify-content: left;
  flex-wrap: wrap;
}

.tag-container {
  display: flex;
  flex-direction: row;
}
.el-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.el-row {
  margin-bottom: 20px;
}


.input-button-wrapper {
  min-width: 80px;
}
.tag-input{
  width:100%;
  display: inline-flex;
}
.control-tools {
  margin-top: 10px;
  display: flex;
  flex-direction: row;
  justify-content: right;
}

.el-text {
  align-self: center;
  justify-self: center;
}
.el-col {
  display: flex;
  justify-content: left;
}


</style>
