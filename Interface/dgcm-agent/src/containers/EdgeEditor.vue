<template>
  <div>
    <div class="common-options">
      <div id="lag-tools">
        <label >Lag: </label>        
        <el-input-number v-model="lag" :min="0" :step="1"></el-input-number>
        <label >(sec.) </label>     
      </div>
      
      <div id="input-len-tools">
        <label >Input Length: </label>    
        <el-input-number v-model="input_len" :min="1"></el-input-number>   
      </div>
    </div>



    <div class="other-options">
      <div id="effect-type-tools" v-if="vCon">
        <el-select label="Effect Type" v-model="scaleSign">
          <el-option
            v-for="item in comp_opts.sign_options" 
            :key="item.key" 
            :value="item.modelValue" 
            :label="item.text">
          </el-option>
        </el-select>  
      </div>

      <div id="scale-edit-tools" v-if="vCon">
        <label for="scale-value-label">Scale:</label>      
        <el-input-number v-model="absScale" :min="0" :max="100" v-bind="comp_opts.scale_num_input"></el-input-number>
      </div>

      <div id="effect-mode-tools" v-if="vCon">
        <el-select label="Effect Mode" v-model="mode">
          <el-option :key="index" :value="item.value" :label="item.text" v-for="item,index in comp_opts.mode_options" />
        </el-select>  
      </div>

      <div id="mapping-tools" v-if="uCatVCat">
        <el-container class="m-4" v-for="(uenc, label) in uValEncode" :key="uenc">
          <el-aside>{{ label }} {{ uenc  }}</el-aside>
          
            <el-main>            
              <el-select
                v-model="mapping[uenc]"
                placeholder="Select"
                style="width: 240px"
              >
              <el-option
                v-for="(venc, label) in vValEncode"
                :key="venc"
                :label="label"
                :value="venc"
              />
            </el-select>
          </el-main>
        </el-container>
      </div>

      <div id="target-value-tools" v-if="uBinVCat">
        <el-select label="Effect Mode" v-model="target_value">
          <el-option
              v-for="(key, value) in uValEncode"
              :key="value"
              :value="value"
              :label="key"
            />
        </el-select>
      </div>



      <div class="spectrum-tools" v-if="uConVCat">
        <div class="flex-container">
          <el-text class="mx-1" size="small">{{ spectrum[0] }}</el-text>
    
          <div v-for="(vInd, index) in Array.from({ length: spectrum.length-2 }, (_, i) => 1 + i)" :key="index">
            <el-dropdown size="small">
                <span class="el-dropdown-link">
                  {{ spectrum[vInd] }}
                  <el-icon class="el-icon--right">
                    <arrow-down/>
                  </el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item disabled>
                      <div class="slider-container">
                        <el-slider 
                        :min="spectrum[vInd-1]"
                        v-model="spectrum[vInd]" 
                        :max="spectrum[vInd+1]"
                        :marks="_getSeptrumSepMarkers(vInd)" />
                      </div>
                     </el-dropdown-item>
                </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            
          
          
          <el-text class="mx-1" size="small">{{ spectrum[spectrum.length-1] }}</el-text>
        </div>
      </div>




      <div id="bounds-tools" v-if="uConVBin">
        <el-container>
          <el-main style="padding: 3rem">
            <el-slider v-model="lowUp" range :step="comp_opts.lowUpStep" :min="uRange[0]" :max="uRange[1]" :marks="lowUpMarks"/>
          </el-main>
        </el-container>
        
      </div>

      <div id="flip-tools" v-if="uBinVBin">
        <el-checkbox v-model="flip"></el-checkbox>
      </div>

      <div id="category-tools" v-if="uCatVBin">
        <el-checkbox
          v-for="key in Object.keys(categoryBools)"
          :key="key"
          v-model="categoryBools[key]"
        >{{ key }}</el-checkbox>
      </div>

    </div>
      
    
    <div class="common-end">
      <el-input type="textarea"
                id="memo" 
                v-model="memo"
                placeholder="(Optional) Further information about this edge..."></el-input>
      <el-checkbox v-model="is_todo" >Mark as TODO</el-checkbox>
      <el-button @click="save">Save</el-button>
      <el-button @click="cancel">Cancel</el-button>
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
    },
    lowUpMarks() {
      return this.uRange.reduce((acc, curr) => {
        acc[curr] = {
          label: curr.toString()
        }
        return acc;
      }, {});
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

        // u Cat
        uValEncode: {}, // { 'valueue-number-input encode }
        vValEncode: {}, // { same as above }


        uCatVCat: false, // categorical to categorical
        mapping: {},    // { int : int }

        uBinVCat: false, // binary to categorical
        target_value: null, 


        uRange: [-999.999, 999.999],
        uConVCat: false, // continous to categorical
        spectrum: [],    // spliter values between the range of variable u

        uConVBin: false,
        lowUp: [-999.999, 999.999],  // continuous to binary
         
        uBinVBin: false, // binary to binary
        flip: false, 

        uCatVBin: false, // categorical to binary 
        category: [],    // this list whose inclusion indicates 1
        categoryBools: {}

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
            ],
            lowUpStep: 0.001
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


      // u Cat: 
      this.uValEncode = dbEdge.uValEncode !== undefined ? dbEdge.uValEncode : defaults.uValEncode;
      

      // u Cat v Con
      this.mapping = dbEdge.mapping !== undefined ? dbEdge.mapping : this._getNullMappingForU();
      console.log(this.mapping);
      

      // u Bin v Cat
      this.vValEncode = dbEdge.vValEncode !== undefined ? dbEdge.vValEncode : defaults.vValEncode;
      this.target_value = dbEdge.target_value !== undefined ? dbEdge.target_value : defaults.target_value;

      // u Con v Cat
      this.uRange = dbEdge.uRange !== undefined ? dbEdge.uRange : defaults.uRange;
      if (dbEdge.spectrum !== undefined) {
        this.spectrum = dbEdge.spectrum;
        this.uRange = [this.spectrum[0], this.spectrum[this.spectrum.length - 1]] // TODO: warn about this
      }
      else {
        console.log(this.vValEncode)
        console.log(dbEdge.vValEncode)
        this.spectrum = this._splitRangeWithBounds(this.uRange, Object.keys(this.vValEncode).length);
      }
      console.log(this.spectrum);
      

      // u Con v Bin
      const up = dbEdge.up !== undefined ? dbEdge.up : defaults.lowUp[1];
      const low = dbEdge.low !== undefined ? dbEdge.low : defaults.lowUp[0];

      const upSd = this._getSmallestDecimal(up);
      const lowSd = this._getSmallestDecimal(low);
      this.comp_opts.lowUpStep = Math.min(Math.min(upSd, lowSd), this.comp_opts.lowUpStep);

      this.lowUp = [low, up]

      

      // u Bin v Bin
      this.flip = dbEdge.flip !== undefined ? dbEdge.flip : defaults.flip;

      // u Cat v Bin
      const category = dbEdge.category !== undefined ? dbEdge.category : defaults.category;
      for (let key in this.uValEncode) {
          this.categoryBools[key] = category.includes(key);
      }
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
        attr.up = this.lowUp[1];
        attr.low = this.lowUp[0];
      }
      
      if (this.uBinVBin) {
        attr.flip = this.flip;
      }

      if (this.uCatVBin) {
        attr.category = Object.keys(this.categoryBools).filter(key => this.categoryBools[key] === true);
      }
      // #endregion

      return {
        edit_type: this.edit_type,
        data: {
          ...baseInfo,
          attr: attr,
        }
      }
      
    },

    _splitRangeWithBounds(usrRange, n) {
        const start = usrRange[0];
        const end = usrRange[usrRange.length - 1];
        if (n === 0) {
            return usrRange;
        }

        const step = (end - start) / n;
        const separators = [];

        for (let i = 0; i < n; i++) {
            const sep = start + step * i 
            separators.push(parseFloat(sep.toFixed(3)));
        }
        separators.push(usrRange[usrRange.length-1])

        return separators;
    },
    _getSmallestDecimal(num) {
        const strNum = num.toString();
        if (!strNum.includes('.')) return 1;
        const decimalPart = strNum.split('.')[1];
        const trimmedDecimal = decimalPart.replace(/0+$/, '');
        const dp = Math.min(6,trimmedDecimal.length)
        return 1 /  Math.pow(10, dp);
    },

    _getSeptrumSepMarkers(index) {
      const slicedArr = [this.spectrum[index - 1], this.spectrum[index + 1]];

      const obj = slicedArr.reduce((accumulator, currentValue) => {
        accumulator[currentValue] = currentValue.toString();
        return accumulator;
      }, {});

      return obj;
    },

    _getNullMappingForU() {
      // Create a new object with keys from the original object and values set to null
      const newObject = {};

      for (const label in this.uValEncode) {
        newObject[this.uValEncode[label]] = '';
      }

      return newObject;
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
  min-width: 200px; 
  margin-left: 18px; 
  margin-right: 18px; 
  min-height: 50px;
}

.flex-container {
  display: flex;
  justify-content: space-between;
}
</style>
