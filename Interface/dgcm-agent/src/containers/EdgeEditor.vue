<template>
  <div>
    <div class="common-options">
      <div id="lag-tools">
        <label >Lag: </label>        
        <vs-input-number v-model="lag" :min="0" :step="1"></vs-input-number>
        <label >(sec.) </label>     
      </div>
      
      <div id="input-len-tools">
        <label >Input Length: </label>    
        <vs-input-number v-model="input_len" min=1></vs-input-number>   
      </div>
    </div>



    <div class="other-options">
      <div id="effect-type-tools" v-if="vCon">
        <vs-select label="Effect Type" v-model="scaleSign">
          <vs-select-item 
            v-for="item in comp_opts.sign_options" 
            :key="item.key" 
            :modelValue="item.modelValue" 
            :text="item.text">
          </vs-select-item>
        </vs-select>  
      </div>

      <div id="scale-edit-tools" v-if="vCon">
        <label for="scale-value-label">Scale:</label>      
        <vs-input-number v-model="absScale" :min="0" :max="100" v-bind="comp_opts.scale_num_input"></vs-input-number>
      </div>

      <div id="effect-mode-tools" v-if="vCon">
        <vs-select label="Effect Mode" v-model="mode">
          <vs-select-item :key="index" :modelValue="item.value" :text="item.text" v-for="item,index in comp_opts.mode_options" />
        </vs-select>  
      </div>

      <div id="mapping-tools" v-if="uCatVCat">
        Not Supposed to be Here
      </div>

      <div id="target-value-tools" v-if="uBinVCat">
        Not Supposed to be Here
      </div>

      <div id="spectrum-tools" v-if="uConVCat">
        Not Supposed to be Here
      </div>

      <div id="bounds-tools" v-if="uConVBin">
        Not Supposed to be Here
      </div>

      <div id="flip-tools" v-if="uBinVBin">
        Not Supposed to be Here
      </div>

      <div id="category-tools" v-if="uCatVBin">
        Not Supposed to be Here
      </div>

    </div>
      
    
    <div class="common-end">
      <vs-textarea label="Memo" id="memo" v-model="memo"></vs-textarea>
      <vs-checkbox v-model="is_todo" >Mark as TODO</vs-checkbox><vs-button @click="save">Save</vs-button>
      <vs-button @click="cancel">Cancel</vs-button>
    </div>
      

  </div>
</template>

<script>


export default {

  data() {
    return {
      ...this.defaultEdge(),
      comp_opts: this.defaultOptions(),
      edit_type: null,
    };
  },

  computed: {
    scale() {
      return this.absScale * this.scaleSign;
    }
  },

  methods: {
    defaultEdge() {
      return {
        // Common fields
        lag: 0,
        old_lag: 0,
        memo: '',
        u: '',
        v: '',
        is_todo: false,
        input_len: 1,

        vCon: false, // if v type is continuous
        effect_len: 1,
        absScale: 1,
        mode: 'grad', // 'value', 'add', 'diff', 'grad'
        scaleSign: 1,

        uCatVCat: false, // categorical to categorical
        uValEncode: {}, // { 'value name': number encode }
        vValEncode: {}, // { same as above }
        mapping: {},    // { int : int }

        uBinVCat: false, // binary to categorical
        target_value: null, 

        uConVCat: false, // continous to categorical
        spectrum: [],    // spliter values between the range of variable u

        uConVBin: false,
        up: Infinity,  // continuous to binary
        low: -Infinity, // continuous to binary

        uBinVBin: false, // binary to binary
        flip: false, 

        uCatVBin: false, // categorical to binary 
        category: [],    // this list whose inclusion indicates 1

      };
    },

    defaultOptions() {
      return {
            scale_num_input: {
              step: 0.000001
            },
            // step_options: Array.from({ length: 6 }, (_, i) => ({ text: `${(1/Math.pow(10, (i + 1))).toFixed(i + 1)}`, value: 1/Math.pow(10, (i + 1)) })),
            mode_options: [ { text: "difference", value: 'diff' }, 
                            { text: "gradient", value: 'grad' }, 
                            { text: "addition", value: 'add' }, 
                            { text: "value", value: 'value' }, ],
            sign_options: [
              { key: 0, modelValue: -1, text: '-' },
              { key: 1, modelValue: 1, text: '+' }
            ]
        };
    },

    setData(uType, vType, dbEdge) {
      const defaults = this.defaultEdge();

      this._setEditorType(uType, vType);

      this._setEditorState(dbEdge, defaults);
    },

    setEditMode(editMode) {
      this.edit_type = editMode;
    },

    save() {
      // Emit or save the edge data as required
      this.$emit('save-edge', this._constructSavingData());
    },

    cancel() {
      this.$emit('cancel-edge')
    },


    _setEditorType(uType, vType) {
      this.vCon = false;     // line a
      this.uCatVBin = false;
      this.uBinVBin = false;
      this.uConVBin = false;
      this.uCatVCat = false;
      this.uBinVCat = false;
      this.uConVCat = false; // line b
      // line b - line a = 7 = 3**2 - 2

      if (vType === 'continuous') {
        this.vCon = true;
      }

      if (vType === 'binary') {
        if (uType === 'categorical') {
          this.uCatVBin = true;
        }
        if (uType === 'binary') {
          this.uBinVBin = true;
        }
        if (uType === 'continuous') {
          this.uConVBin = true;
        }
      }

      if (vType === 'categorical') {
        if (uType === 'categorical') {
          this.uCatVCat = true;
        }
        if (uType === 'binary') {
          this.uBinVCat = true;
        }
        if (uType === 'continuous') {
          this.uConVCat = true;
        }
        
      }
    },

    _setEditorState(dbEdge, defaults) {
        console.log(dbEdge);
        // #region basic settings
        this.u = dbEdge.from !== undefined ? dbEdge.from : defaults.from;
        this.v = dbEdge.to !== undefined ? dbEdge.to : defaults.to;
        console.log(dbEdge.lag);
        this.lag = dbEdge.lag !== undefined ? dbEdge.lag : defaults.lag;
        this.old_lag = this.lag;

        this.memo = dbEdge.memo !== undefined ? dbEdge.memo : defaults.memo;
        this.input_len = dbEdge.input_len !== undefined ? dbEdge.input_len : defaults.input_len;
        this.is_todo = dbEdge.is_todo !== undefined ? dbEdge.is_todo: defaults.is_todo;
        // #endregion

        // scale 
        // #region  vType = continuous
        const dbScale = dbEdge.scale !== undefined ? dbEdge.scale : defaults.scale;
        this.absScale = Math.abs(dbScale);
        this.scaleSign = dbScale >= 0? 1 : -1
        this.mode = dbEdge.mode !== undefined ? dbEdge.mode : defaults.mode;
        this.effect_len = dbEdge.effect_len !== undefined ? dbEdge.effect_len : defaults.effect_len;
        // #endregion

        // u Cat v Con
        this.mapping = dbEdge.mapping !== undefined ? dbEdge.mapping : defaults.mapping;
        this.uValEncode = dbEdge.uValEncode !== undefined ? dbEdge.uValEncode : defaults.uValEncode;
        this.vValEncode = dbEdge.vValEncode !== undefined ? dbEdge.vValEncode : defaults.vValEncode;

        // u Bin v Cat
        this.target_value = dbEdge.target_value !== undefined ? dbEdge.target_value : defaults.target_value;

        // u Con v Cat
        this.spectrum = dbEdge.spectrum !== undefined ? dbEdge.spectrum : defaults.spectrum;

        // u Con v Bin
        this.up = dbEdge.up !== undefined ? dbEdge.up : defaults.up;
        this.low = dbEdge.low !== undefined ? dbEdge.low : defaults.low;

        // u Bin v Bin
        this.flip = dbEdge.flip !== undefined ? dbEdge.flip : defaults.flip;

        // u Cat v Bin
        this.category = dbEdge.category !== undefined ? dbEdge.category : defaults.category;
    },

    _constructSavingData() { 
      const baseInfo = {
        from: this.u, 
        to: this.v,
        lag: this.lag, 
        old_lag: this.old_lag,
      }
      const attr = {
        input_len: this.input_len,
        is_todo: this.is_todo,
        memo: this.memo,
      }

      // #region long switch cases
      if (this.vCon) {
        attr.scale = this.scale;
        attr.effect_len = this.effect_len;
        attr.mode = this.mode;
        attr.effect_type = this.mode;
      }

      if (this.uCatVCat) {
        attr.mapping = this.mapping;
      }

      if (this.uBinVCat) {
        attr.target_value = this.target_value;
      }

      if (this.uConVCat) {
        attr.spectrum = this.spectrum;
      } // continous to categorical

      if (this.uConVBin) {
        attr.up = this.up;
        attr.low = this.low;
      }
      
      if (this.uBinVBin) {
        attr.flip = this.flip;
      }

      if (this.uCatVBin) {
        attr.category = this.category;
        attr.category = this.category;
      }
      // #endregion

      return {
        edit_type: this.edit_type,
        data: {
          ...baseInfo,
          attr: attr,
        }
      }
      
    }
  }  


}

</script>

<style scoped>
.edge-editor-popup {
  background-color: white;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border-radius: 5px;
}
.common-options {
  margin: 10px;
}

.superscript {
  vertical-align: super;
  font-size: smaller;
}
.vs-row {
  height: 30px;
  margin: 2%;
}



.step-dropdown {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 80px;
}

.step-dropdown .a-icon {
  outline: none;
  text-decoration: none !important;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-dropdown .a-icon i {
  font-size: 18px;
}

.vs-dropdown-menu .con-input {
  margin-bottom: 20px;
}

.step-dropdown .base-content h3 {
  color: rgba(0, 0, 0, 0.5);
  text-align: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding-bottom: 5px;
}

.step-dropdown .base-content p {
  max-width: 200px;
  font-size: 11px;
  padding: 5px;
}
.slider-container {
  margin: 10px;
}

</style>
