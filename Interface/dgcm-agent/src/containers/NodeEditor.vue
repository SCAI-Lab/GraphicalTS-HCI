<template>
  <div>
      <div class="node-options">
        
          <label for="nodeName">Node Name</label>
          <vs-input placeholder="Placeholder" v-model="nodeName"/>
          
          <vs-select v-model="nodeType">
            <vs-select-item :key="item.key" :modelValue="item.modelValue" :text="item.text" v-for="item in comp_opts.typeOptions" ></vs-select-item>
          </vs-select>

          <div id="category-tools" v-if="nodeType==='categorical'">
            <vs-chips color="rgb(145, 32, 159)" placeholder="Type Element Name and Hit Enter" v-model="valChips">
              <vs-chip
                :key="chip"
                @click="_remove(chip)"
                v-for="chip in valChips" closable>
                {{ chip }}
              </vs-chip>
            </vs-chips>
          </div>
          
          <div id="range-tools" v-if="nodeType==='continuous'">
            <vs-input-number :min="valRange[0]" :max="valRange[1]" :step=1></vs-input-number>
          </div>


          <label for="memo">Memo for this Node</label>
          <vs-textarea id="memo" v-model="memo"></vs-textarea>

          <vs-button @click="save">Save</vs-button>
          <vs-button @click="cancel">Cancel</vs-button>
      </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      ...this.defaultNode(),
      edit_type: null,
      comp_opts: this.defaultOptions()
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
        ]
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

      this.valRange = dbNode.bounds !== undefined? dbNode.bounds: defaults.valRange;
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
      this.valChips.splice(this.chips.indexOf(item), 1)
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
</style>
