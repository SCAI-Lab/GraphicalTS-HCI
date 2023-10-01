<template>
    <div id="upload-container">
      <vs-row vs-justify="center">
      <vs-col vs-type="flex" vs-justify="center" vs-align="center" vs-w="6"><input type="file" @change="onFileChange" ref="fileInput"></vs-col>
      <vs-col vs-type="flex" vs-justify="center" vs-w="3"><vs-button @click="uploadFile" :disabled="!selectedFile">Upload</vs-button></vs-col>
      </vs-row>
      <p v-if="uploadStatus">{{ uploadStatus }}</p>
    </div>
  </template>

  <style>
  

  </style>
  
  <script>
  import apiClient from '@/axiosConfig.js';


  export default {
    data() {
      return {
        selectedFile: null,
        uploadStatus: ''
      };
    },
    methods: {
        // 
        onFileChange(e) {
            const files = e.target.files || e.dataTransfer.files;
            if (!files.length) return;
            this.selectedFile = files[0];
        },

        // upload  file using the upload API
        async uploadFile() {
            // * Check existence
            if (!this.selectedFile) {
                this.uploadStatus = 'Please select a file first!';
                return;
            }
            // * there is a selected file then get it
            const formData = new FormData();
            formData.append('file', this.selectedFile);

            // * param the selected file and post
            apiClient.post("/upload", formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            }).then(response => {
                this.uploadStatus = 'File uploaded successfully!';
                this.$refs.fileInput.value = '';  // Reset file input
                this.$emit("new-uploaded", response.data.graph_name)
                console.log(response)
            }).catch(error => {
                this.uploadStatus = 'Error uploading file: ' + error;
            });

        },


    }
  };
  </script>
  
  <style>
#upload-container {
  justify-content: center;
}

</style>