<template>
  <div ref="editorContainer" class="monaco-editor"></div>
</template>

<script>
import * as monaco from 'monaco-editor';
import { onMounted, onUnmounted, ref, watch } from 'vue';

export default {
  props: {
    value: String,
    language: {
      type: String,
      default: 'javascript'
    },
    theme: {
      type: String,
      default: 'vs-dark'
    },
    options: {
      type: Object,
      default: () => ({})
    },
    height: {
      type: String,
      default: '300px'
    }
  },
  emits: ['update:value'],
  setup(props, { emit }) {
    const editorContainer = ref(null);
    let editor = null;

    onMounted(() => {
      editor = monaco.editor.create(editorContainer.value, {
        value: props.value,
        language: props.language,
        theme: props.theme,
        ...props.options
      });

      editor.onDidChangeModelContent(() => {
        emit('update:value', editor.getValue());
      });
    });

    onUnmounted(() => {
      editor?.dispose();
    });

    watch(() => props.value, (newValue) => {
      if (editor && editor.getValue() !== newValue) {
        editor.setValue(newValue);
      }
    });

    return { editorContainer };
  }
};
</script>

<style scoped>
.monaco-editor {
  width: 100%;
  height: v-bind(height);
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>