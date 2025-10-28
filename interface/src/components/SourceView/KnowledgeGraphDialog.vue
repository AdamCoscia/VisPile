<template>
  <v-card title="Knowledge Graph" subtitle="Search for nodes and links" :prepend-icon="mdiGraphOutline">
    <template v-slot:append>
      <v-btn :icon="mdiClose" @click="isActive = false"></v-btn>
    </template>

    <v-card-text>
      <div class="d-flex" style="gap: 12px">
        <!-- NODES -->
        <div style="flex: 0 0 200px">
          <!-- SEARCH -->
          <v-autocomplete
            v-model="selectedNode"
            :hint="nodesHintText"
            :items="knowledgeGraph.nodes"
            item-title="id"
            class="my-2"
            label="Search nodes"
            variant="outlined"
            density="comfortable"
            clearable
            return-object
            persistent-hint
          ></v-autocomplete>

          <!-- LIST -->
          <div class="node-list-wrapper">
            <v-virtual-scroll :items="filteredNodes" class="py-1" height="320" item-height="50">
              <template v-slot:default="{ item }">
                <v-list-item @click="selectedNode = item">
                  <v-list-item-title class="list-item-title">{{ item.id }}</v-list-item-title>
                  <v-list-item-subtitle>
                    <div>Degree: {{ item.degree }}</div>
                    <div>Closeness: {{ formatNumber(item.closeness * 100, 2) }}%</div>
                    <div>Rank: {{ formatNumber(item.rank * 100, 2) }}%</div>
                  </v-list-item-subtitle>
                </v-list-item>
              </template>
            </v-virtual-scroll>
          </div>

          <!-- SORT -->
          <v-select
            v-model="nodesSortBy"
            :items="['degree', 'closeness', 'rank']"
            :disabled="selectedNode !== null"
            class="mt-4"
            label="Sort nodes"
            density="compact"
            variant="outlined"
            clearable
            hide-details
          >
          </v-select>
        </div>

        <!-- TABLE -->
        <div class="overflow-auto" style="width: 100%">
          <v-text-field
            v-model="linkTableSearch"
            :hint="linksHintText"
            :prepend-inner-icon="mdiMagnify"
            class="my-2"
            label="Search links"
            density="comfortable"
            variant="outlined"
            clearable
            persistent-hint
          ></v-text-field>
          <v-data-table :headers="linkTableHeaders" :items="filteredLinks" :search="linkTableSearch" height="350">
            <template v-slot:item.source="{ item }">
              <div class="table-cell" @click="selectedNode = knowledgeGraph.nodes.find((n) => n.id == item.source)">
                {{ item.source }}
              </div>
            </template>
            <template v-slot:item.target="{ item }">
              <div class="table-cell" @click="selectedNode = knowledgeGraph.nodes.find((n) => n.id == item.target)">
                {{ item.target }}
              </div>
            </template>
            <template v-slot:item.document="{ item }">
              <v-chip density="comfortable" label @click="activeNode = item">
                {{ nodeData[item.document].name }}
              </v-chip>
            </template>
          </v-data-table>
        </div>
      </div>

      <!-- ACTIVE NODE TEXT -->
      <v-expand-transition>
        <div v-show="activeNode !== null" class="mt-2">
          <v-card elevation="3">
            <v-card-text>
              <div class="d-flex align-end justify-space-between">
                <span>{{ activeNodeTitle }}</span>
                <v-btn :icon="mdiClose" density="comfortable" size="small" @click="activeNode = null"></v-btn>
              </div>
              <v-divider class="my-2"></v-divider>
              <div v-html="activeNodeHTML" class="node-text"></div>
            </v-card-text>
          </v-card>
        </div>
      </v-expand-transition>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, inject, computed } from "vue";
import * as d3 from "d3";
import { formatNumber, removeExtraNewlines, highlightText } from "@/utils";
import { mdiGraphOutline, mdiClose, mdiMagnify } from "@mdi/js";

// get providers
const { documents } = inject("documents");
const { searchTerms, searchTermSettings } = inject("searchTerms");
const { entity } = inject("entity");
const { knowledgeGraph } = inject("knowledgeGraph");

// get props
const props = defineProps(["isActive"]);

// get refs
const nodeData = ref({}); // node data look up
const selectedNode = ref(null);
const nodesSortBy = ref(null);
const activeNode = ref(null); // node that is currently clicked
const linkTableSearch = ref("");
const linkTableHeaders = ref([
  { key: "source", title: "Source" },
  { key: "label", title: "Label" },
  { key: "target", title: "Target" },
  { key: "document", title: "Document" },
]);

nodeData.value = Object.fromEntries(
  documents.value.map((d) => {
    return [d.id, d];
  })
);

const isActive = props.isActive;

// get computed
const filteredNodes = computed(() => {
  let newNodes = knowledgeGraph.value.nodes;
  // filter
  if (selectedNode.value !== null) {
    newNodes = newNodes.slice().filter((node) => node.id == selectedNode.value.id);
  }
  // sort (only when node is not selected)
  if (selectedNode.value == null && nodesSortBy.value !== null) {
    switch (nodesSortBy.value) {
      case "degree": {
        newNodes = newNodes.slice().sort((a, b) => d3.descending(a.degree, b.degree));
        break;
      }
      case "closeness": {
        newNodes = newNodes.slice().sort((a, b) => d3.descending(a.closeness, b.closeness));
        break;
      }
      case "rank": {
        newNodes = newNodes.slice().sort((a, b) => d3.descending(a.rank, b.rank));
        break;
      }
    }
  }
  return newNodes;
});
const filteredLinks = computed(() => {
  let newLinks = knowledgeGraph.value.links;
  // filter
  if (selectedNode.value !== null) {
    newLinks = newLinks
      .slice()
      .filter((link) => link.source == selectedNode.value.id || link.target == selectedNode.value.id);
  }
  return newLinks;
});
const nodesHintText = computed(() => {
  let numNodes = filteredNodes.value.length;
  return `Found ${numNodes} nodes.`;
});
const linksHintText = computed(() => {
  let numLinks = filteredLinks.value.length;
  if (linkTableSearch.value) {
    numLinks = filteredLinks.value.filter((link) => {
      return (
        String(link.source).toLowerCase().includes(linkTableSearch.value.toLowerCase()) ||
        String(link.label).toLowerCase().includes(linkTableSearch.value.toLowerCase()) ||
        String(link.target).toLowerCase().includes(linkTableSearch.value.toLowerCase()) ||
        String(link.document).toLowerCase().includes(linkTableSearch.value.toLowerCase())
      );
    }).length;
  }
  return `Found ${numLinks} links.`;
});
const activeNodeTitle = computed(() => {
  if (activeNode.value !== null) {
    return nodeData.value[activeNode.value.document].name;
  }
  return "";
});
const activeNodeHTML = computed(() => {
  if (activeNode.value !== null) {
    const text = nodeData.value[activeNode.value.document].text;
    const clean = removeExtraNewlines(text);
    const terms = [
      ...searchTerms.value.map((term) => {
        return { text: term, termClassName: "search-term", patternType: searchTermSettings.value.patternMatch };
      }),
    ];
    if (entity.value.name !== null) {
      terms.push({ text: entity.value.name, termClassName: "entity-term", patternType: "whole-word" });
    }
    const html = highlightText(clean, terms);
    return html;
  }
  return "";
});
</script>

<style lang="scss">
.node-list-wrapper {
  border: 1px solid rgba(0, 0, 0, 0.32);
  border-radius: 4px;

  .list-item-title {
    padding-bottom: 4px;
    white-space: pre-wrap !important;
    line-height: 1rem !important;
  }
}

.table-cell {
  transition: all 200ms;
  cursor: pointer;
}
.table-cell:hover {
  background-color: rgba(0, 0, 0, 0.04);
}
</style>
