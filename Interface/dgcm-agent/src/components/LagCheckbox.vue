<template>
  <div id="lagbox-container">
    <input  class="lag-checkbox"
            type="checkbox"
           :name="'edgesFilter'"
           :value="lag"
           v-model="isChecked"
           @change="emitChange"
           ref="cb">
    <label id="lag-label">{{ lag }}</label>
  </div>
</template>

<script>
export default {
  props: ['lag', 'color', 'initialChecked'],
  data() {
    return {
      isChecked: this.initialChecked
    }
  },
  mounted() {
    this.$refs.cb.style.setProperty('--color', this.color);
  },
  watch: {
    initialChecked(newVal) {
      this.isChecked = newVal;
      this.emitChange();
    }
  },
  methods: {
    emitChange() {
      this.$emit('checkbox-changed', {lag: this.lag, checkState: this.isChecked});
    }
  }
}
</script>

<style>

.lag-checkbox[type=checkbox] {
    width: 1.6rem;
    height: 1.6rem;
    color: rgb(134, 134, 134);
    vertical-align: middle;
    -webkit-appearance: none;
    background: none;
    border: 0;
    outline: 0;
    flex-grow: 0;
    border-radius: 50%;
    background-color: #FFFFFF;
    transition: background 300ms;
    cursor: pointer;
  }
  
  /* Pseudo element for check styling */
  
  .lag-checkbox[type=checkbox]::before {
    content: "";
    color: transparent;
    display: block;
    width: inherit;
    height: inherit;
    border-radius: inherit;
    border: 0;
    background-color: transparent;
    background-size: contain;
    box-shadow: inset 0 0 0 1px #CCD3D8;
  }
  
  /* Checked */
  .lag-checkbox[type=checkbox]:checked {
    background-color: var(--color);
  }
  
  .lag-checkbox[type=checkbox]:checked::before {
    box-shadow: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E %3Cpath d='M15.88 8.29L10 14.17l-1.88-1.88a.996.996 0 1 0-1.41 1.41l2.59 2.59c.39.39 1.02.39 1.41 0L17.3 9.7a.996.996 0 0 0 0-1.41c-.39-.39-1.03-.39-1.42 0z' fill='%23fff'/%3E %3C/svg%3E");
  }
  
  /* Disabled */
  .lag-checkbox[type=checkbox]:disabled {
    background-color: #CCD3D8;
    opacity: 0.84;
    cursor: not-allowed;
  }
  
  /* IE */
  .lag-checkbox[type=checkbox]::-ms-check {
    content: "";
    color: transparent;
    display: block;
    width: inherit;
    height: inherit;
    border-radius: inherit;
    border: 0;
    background-color: transparent;
    background-size: contain;
    box-shadow: inset 0 0 0 1px #CCD3D8;
  }
  
  .lag-checkbox[type=checkbox]:checked::-ms-check {
    box-shadow: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E %3Cpath d='M15.88 8.29L10 14.17l-1.88-1.88a.996.996 0 1 0-1.41 1.41l2.59 2.59c.39.39 1.02.39 1.41 0L17.3 9.7a.996.996 0 0 0 0-1.41c-.39-.39-1.03-.39-1.42 0z' fill='%23fff'/%3E %3C/svg%3E");
  }
  
  #lagbox-container {
    display: flex;
    align-items: center;
    margin: 5px;
  }
  
  #lag-label {
    display: flex;
    align-items: center;
    float: right;
    width: 50%;
    text-align: left;
    height: auto;
    justify-content: center;
    /* text-anchor: middle; */
  }

</style>

