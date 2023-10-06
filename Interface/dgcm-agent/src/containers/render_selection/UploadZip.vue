<template>
    <el-upload 
      ref="myUpload"
      :auto-upload="false"
      drag
      multiple
      action=""
      :http-request="handleSelected"
      accept=".zip"
      :v-model="fileList">
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        Drop file here or <em>click to upload</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          zip files with a size less than 500kb
        </div>
      </template>
    </el-upload>
    <el-button @click="submitUpload">
          Upload Selected Files
    </el-button>
  </template>

  <style>
  

</style>

<script>
import apiClient from '@/axiosConfig.js';


export default {
  data() {
    return {
      uploadStatus: '',
      fileList: [],
    };
  },
  methods: {

      async handleSelected(options) {
        const formData = new FormData();
        formData.append('file', options.file);

        // * param the selected file and post
        return apiClient.post("/upload", formData, {
              headers: {
                  'Content-Type': 'multipart/form-data'
              }
          }).then(response => {
              this.uploadStatus = 'File uploaded successfully!';
              this.$emit("new-uploaded", response.data.graph_name);
          }).catch(error => {
              this.uploadStatus = 'Error uploading file: ' + error;
        });
    },
    submitUpload() {
      this.$refs.myUpload.submit();
    }
  }
}

</script>
  
<style>
#upload-container {
  justify-content: center;
}

</style>