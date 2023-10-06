<template>
  <div>

    <div id="basic-info">
      <div class="common-options">
        <h3>Basic Infomation</h3>
        <el-row style="justify-items: center;">
          <el-col :span="5">
            <el-text>Lag:</el-text>
          </el-col>
          <el-col :span="16">
            <el-input-number v-model="lag" :min="0" :step="1" controls-position="right"></el-input-number>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="5">
            <el-text>Input Length:</el-text>
          </el-col>
          <el-col :span="16">
            <el-input-number v-model="input_len" :min="1" controls-position="right" :disabled="!vCon"></el-input-number>
          </el-col>
        </el-row>

      </div>
    </div>

    <div id="comb-options">

      <div class="common-options" v-if="vCon">
        <h3>Options for Mapping to a Continuous Variable</h3>
        <div id="scale-sign-tools" >
          <el-row>
            <el-col :span="5">
              <el-text>Effect Direction:</el-text>
            </el-col>
            <el-col :span="16">
              <el-radio-group v-model="scaleSign">
                <el-radio label="+">Positive Effect</el-radio>
                <el-radio label="-">Negative Effect</el-radio>
              </el-radio-group>
            </el-col>
          </el-row>
        </div>

        <div id="scale-val-tools" >
          <el-row>
            <el-col :span="5">
              <el-text>Effect Scale:</el-text>
            </el-col>
            <el-col :span="8">
              <el-button @click="changeSign">
                <el-icon>
                  <Plus v-if="scaleSign==='+'" />
                  <Minus v-if="scaleSign==='-'" />
                </el-icon>
              </el-button>
              <el-input-number v-model="absScale" :min="0" :max="100" v-bind="comp_opts.scale_num_input"
                controls-position="right">
              </el-input-number>
            </el-col>

          </el-row>
        </div>

        <div id="effect-mode-tools" >
          <el-row>
            <el-col :span="5">
              <el-text>Setting Mode:</el-text>
            </el-col>
            <el-col :span="19">
              <el-radio-group v-model="mode">
                <el-radio v-for="item,index in comp_opts.mode_options" :key="index" :label="item.value">
                  {{ item.text }}
                </el-radio>
              </el-radio-group>
            </el-col>
          </el-row>

        </div>

        <div id="effect-len-tools">
          <el-row>
            <el-col :span="5">
              <el-text>Effect Duration:</el-text>
            </el-col>
            <el-col :span="8">
              <el-input-number v-model="effect_len" :min="0" :max="100" controls-position="right">
              </el-input-number>
            </el-col>

          </el-row>
        </div>
      </div>

      <div class="common-options" v-if="uCatVCat">
        <h3>Options for Categorical to Categorical Edge</h3>
        <div id="mapping-tools">
          <el-row> 
            <el-col :span="8" style="justify-content: center;">{{ u }}</el-col>
            <el-col :span="2"></el-col>
            <el-col :span="11" style="justify-content: center;">{{ v }}</el-col>
          </el-row>
          <el-row v-for="(uenc, label) in uValEncode" :key="uenc">
            <el-col :span="8" style="justify-content: center;"><el-text>{{ label }}</el-text></el-col>
            <el-col :span="2" style="align-items: center; justify-content: center;"><el-icon><Right/></el-icon></el-col>
            <el-col :span="11">
              <el-select v-model="mapping[uenc]" placeholder="Select" style="width: 240px">
                <el-option v-for="(venc, label) in vValEncode" :key="venc" :label="label" :value="venc" />
              </el-select>
            </el-col>
          </el-row>
        </div>
      </div>

      <div class="common-options" v-if="uBinVCat">
        <div id="target-value-tools">
          <el-select label="Effect Mode" v-model="target_value">
            <el-option v-for="(key, value) in uValEncode" :key="value" :value="value" :label="key" />
          </el-select>
        </div>
      </div>

      <div class="common-options" v-if="uConVCat">
        <h3>Options for Mapping Continuous to Categorical</h3>
        <div class="spectrum-tools">
          <div class="flex-container">
            <el-row :gutter="5" style="justify-content: center;">
              <el-col :span="3"><el-text class="mx-1" size="small">{{ uRange[0] }}</el-text></el-col>
              <el-col v-for="_, index in mapping" 
                      :key="index" 
                      :span="index < spectrum.length? Math.round(38/(2*Object.keys(mapping).length - 1)): 
                                                      Math.round(19/(2*Object.keys(mapping).length - 1)) ">

                <el-col :span="index < spectrum.length? 12 : 24">
                  <el-select v-model="mapping[index]" @change="(value) => {
                    console.log(value);
                  }">
                    <el-option
                      v-for="(cItem, cInd) in keysToLocate"
                      :key="cInd"
                      :label="cItem"
                      :value="cItem"
                    />
                  </el-select>
                </el-col>

                <el-col :span="12" v-if="index < spectrum.length">
                  <el-dropdown size="small">
                    <span class="el-dropdown-link">
                      {{ spectrum[parseInt(index)] }}
                      <el-icon class="el-icon--right">
                        <arrow-down />
                      </el-icon>
                    </span>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item disabled>
                          <div class="slider-container">
                            <el-slider :min="parseInt(index) === 0? uRange[0]: spectrum[parseInt(index)-1]" 
                                      v-model="spectrum[parseInt(index)]" 
                                      :max="parseInt(index) === spectrum.length-1? uRange[1]: spectrum[parseInt(index)+1]"
                                      :marks="_getSeptrumSepMarkers(parseInt(index))"
                                      :step="0.01"
                              />
                          </div>
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </el-col>

              </el-col>
              <el-col :span="3"><el-text class="mx-1" size="small">{{ uRange[1] }}</el-text></el-col>
            </el-row>
            
          </div>
        </div>
      </div>

      <div class="common-options" v-if="uConVBin">
        <h3>Options for Mapping Continuous to Binary</h3>
        <div id="bounds-tools">
          <el-row>
            <el-col :span="24">Range of Activation: <b>{{ lowUp[0] }} ~ {{ lowUp[1] }}</b>  (slide to adjust)</el-col>
          </el-row>
          <el-row style="padding-left:10px; padding-right:10px;">
            <el-slider v-model="lowUp" range :step="comp_opts.lowUpStep" :min="uRange[0]" :max="uRange[1]"
                :marks="lowUpMarks" />
          </el-row>

        </div>
      </div>

      <div class="common-options" v-if="uBinVBin">
        <h3>Options for Mapping Binary to Binary</h3>
        <div id="flip-tools">
          <el-row>
            <el-col :span="8"><el-text>Opposite Trigger ?</el-text></el-col>
            <el-col :span="8">          
              <el-radio-group v-model="flip" >
                <el-radio :label="true">Yes</el-radio>
                <el-radio :label="false">No</el-radio>
              </el-radio-group>
            </el-col>
          </el-row>

        </div>
      </div>

      <div class="common-options" v-if="uCatVBin">
        <h3>Options for Mapping Categorical to Binary</h3>
        
        <div id="category-tools">
          <el-row><el-text>Please check the cateogories of <b>{{ u }}</b> that triggers  <b>{{ v }}</b></el-text></el-row>
          <el-row><el-checkbox v-for="key in Object.keys(categoryBools)" :key="key" v-model="categoryBools[key]">{{ key }}
          </el-checkbox></el-row>
        </div>
      </div>

    </div>
    

    <div id="common-end">
      <div class="common-options">
        <h3>Memo for this Node</h3>
        <el-input type="textarea" id="memo" v-model="memo" placeholder="(Optional) Further information about this edge...">
        </el-input>

        <div class="control-tools">
            <el-button @click="save" type="primary">Save</el-button>
            <el-button @click="cancel">Cancel</el-button>
        </div>
      </div>

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
      const signFactor = this.scaleSign === '+'? 1 : -1;
      return this.absScale * signFactor;
    },
    
    lowUpMarks() {
      const marks = this.uRange.reduce((acc, curr) => {
        acc[curr] = {
          label: curr.toString()
        }
        return acc;
      }, {});

      if ( this.uRange[0] < 0 ) {
        marks['0'] = {
          label: '0',
        }
      }

      return marks;
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
        scaleSign: '+',

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
        keysToLocate: [],

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
      this.scaleSign = dbScale >= 0? '+' : '-'
      this.mode = dbEdge.mode !== undefined ? dbEdge.mode : defaults.mode;
      this.effect_len = dbEdge.effect_len !== undefined ? dbEdge.effect_len : defaults.effect_len;
      // #endregion


      // u Cat: 
      this.uValEncode = dbEdge.uValEncode !== undefined ? dbEdge.uValEncode : defaults.uValEncode;
      

      // u Cat v Cat
      this.mapping = dbEdge.mapping !== undefined ? dbEdge.mapping : this._getNullMappingForU();
      console.log(this.mapping);
      

      // u Bin v Cat
      this.vValEncode = dbEdge.vValEncode !== undefined ? dbEdge.vValEncode : defaults.vValEncode;
      this.target_value = dbEdge.target_value !== undefined ? dbEdge.target_value : defaults.target_value;

      // u Con v Cat
      this.uRange = dbEdge.uRange !== undefined ? dbEdge.uRange : defaults.uRange;
      if (dbEdge.spectrum !== undefined) {
        this.spectrum = dbEdge.spectrum;
      }
      else {
        console.log(this.vValEncode)
        console.log(dbEdge.vValEncode)
        this.spectrum = this._splitRangeWithBounds(this.uRange, Object.keys(this.vValEncode).length);
      }
      if (Object.keys(this.mapping).length === 0 && this.uConVCat) {
        this.mapping = this._getSepDefaultMapping(this.spectrum.length+1);
      }
      this.keysToLocate = Object.keys(this.vValEncode);
      console.log(this.spectrum);
      console.log(this.mapping);
      

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
        attr.mapping = this.mapping;
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
        if (n < 0) {
          return 
        }
        const start = usrRange[0];
        const end = usrRange[usrRange.length - 1];

        const step = (end - start) / n;
        const separators = [];



        for (let i = 0; i < n - 1; i++) {
            const sep = start + step * (i+1) 
            separators.push(parseFloat(sep.toFixed(3)));
        }

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
      const start = index === 0 ? this.uRange[0] : this.spectrum[index - 1]
      const end = index === this.spectrum.length - 1 ? this.uRange[1] : this.spectrum[index + 1]
      const slicedArr = [start, end];

      const obj = slicedArr.reduce((accumulator, currentValue) => {
        accumulator[currentValue] = currentValue.toString();
        return accumulator;
      }, {});

      return obj;
    },

    _getSepDefaultMapping(len) {
      const obj = {};
      for (let i = 0; i < len; i++) {
        obj[i] = '';
      }
      return obj;
    },

    _getNullMappingForU() {
      // Create a new object with keys from the original object and values set to null
      const newObject = {};

      for (const label in this.uValEncode) {
        newObject[this.uValEncode[label]] = '';
      }

      return newObject;
    },

    changeSign() {
      this.scaleSign = this.scaleSign === '+'? '-': '+'
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
.other-options{
  display: flex;
  flex-direction: column;;
}

.superscript {
  vertical-align: super;
  font-size: smaller;
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
.el-text {
  align-self: center;
  justify-self: center;
}
.el-col {
  display: flex;
  justify-content: left;
}
.el-row {
  margin-bottom: 20px;
}

#sign-select {
  width: 30px;
}

.control-tools {
  margin-top: 10px;
  display: flex;
  flex-direction: row;
  justify-content: right;
}

</style>
