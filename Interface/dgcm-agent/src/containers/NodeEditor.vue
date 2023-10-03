<template>
  <div>
      <div class="node-options">
        
          <label for="nodeName">Node Name</label>
          <el-input placeholder="Placeholder" v-model="nodeName"/>
          
          <el-select v-model="nodeType">
            <el-option :key="item.key" :value="item.modelValue" :text="item.text" v-for="item in typeOptions"></el-option>
          </el-select>

          <div id="category-tools" v-if="nodeType==='categorical'">
              <el-tag
                :key="chip"
                @close="_remove(chip)"
                closable
                class="mx-1"
                :disable-transitions="false"
                v-for="chip in valChips"
                >
              {{ chip }}
            </el-tag>
            <div class="input-button-wrapper">
              <el-input
                v-if="newItemInputVisible"
                ref="newItemInput"
                v-model="newItemInputValue"
                size="small"
                @keyup.enter="handleInputConfirm"
                @blur="handleInputConfirm"
              ></el-input>
              <el-button v-else size="small" @click="showInput">
                + New Value
              </el-button>
            </div>
          </div>
          
          <div id="range-tools" v-if="nodeType==='continuous'">
            <el-input-number v-model="valRange[0]" :max="valRange[1]"></el-input-number>
            <el-input-number v-model="valRange[1]" :min="valRange[0]"></el-input-number>
          </div>


          <label for="memo">Memo for this Node</label>
          <el-input type="textarea" id="memo" v-model="memo"></el-input>

          <el-button @click="save">Save</el-button>
          <el-button @click="cancel">Cancel</el-button>
      </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      ...this.defaultNode(),
      edit_type: null,
      ...this.defaultOptions()
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
        nodeType: 'continuous',
        is_todo: false,

        valRange: [0, 1], // continuous type  
        valOffset: 0,


        historicalEncode: {},
        valChips: []
        
      };
    },

    defaultOptions() {
      return {
        typeOptions:  [       
          { key: 1, modelValue: 'categorical', text: 'categorical' },
          { key: 0, modelValue: 'continuous', text: 'continuous' },
          { key: 2, modelValue: 'binary', text: 'binary' }
        ],
        newItemInputVisible: false,
        newItemInputValue: '',

      };
    },

    setData(dbNode) {
      const defaults = this.defaultNode();
      this._setEditorState(dbNode, defaults);
    },

    setEditMode(editMode) {
      this.edit_type = editMode;
    },

    save() {
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
        this.valChips.push(this.newItemInputValue)
      }
      this.newItemInputVisible = false;
      this.newItemInputValue = '';
    },
    showInput() {
      this.newItemInputVisible = true;
      this.$nextTick(() => {
        this.$refs.newItemInput.focus();
      })
    }

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
</style>
