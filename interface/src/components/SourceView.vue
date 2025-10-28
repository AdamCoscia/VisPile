<template>
  <v-col class="d-flex flex-column overflow-hidden" style="max-height: 100%">
    <!-- HEADER -->
    <div class="d-flex flex-wrap justify-space-between">
      <!-- TITLE -->
      <header class="sources-title">Documents</header>
    </div>

    <!-- DATA VIEW BUTTONS -->
    <div class="d-flex my-2" style="column-gap: 12px">
      <div>
        <v-dialog persistent>
          <template v-slot:activator="{ props: activatorProps }">
            <v-btn v-bind="activatorProps" :prepend-icon="mdiGraphOutline">Graph</v-btn>
          </template>
          <template v-slot:default="{ isActive }">
            <KnowledgeGraphDialog :is-active="isActive" />
          </template>
        </v-dialog>
      </div>
      <div>
        <v-dialog persistent>
          <template v-slot:activator="{ props: activatorProps }">
            <v-btn v-bind="activatorProps" :prepend-icon="mdiChartScatterPlot">Embeds</v-btn>
          </template>
          <template v-slot:default="{ isActive }">
            <EmbeddingsDialog :is-active="isActive" />
          </template>
        </v-dialog>
      </div>
    </div>

    <v-divider class="my-2"></v-divider>

    <div class="d-flex align-center">
      <div class="flex-1-0" style="font-weight: 700; text-shadow: 2px 2px 1px #2b2b2b">Search settings</div>
      <v-icon
        :icon="showSearchSettings ? mdiUnfoldLessHorizontal : mdiUnfoldMoreHorizontal"
        @click="showSearchSettings = !showSearchSettings"
      ></v-icon>
    </div>

    <v-expand-transition>
      <div v-if="showSearchSettings">
        <!-- FILTER INPUT -->
        <div v-if="documents.length > 0" class="d-flex mt-2">
          <!-- INPUT -->
          <v-combobox
            v-model="searchTerms"
            v-model:search="currentSearchTerm"
            :hide-no-data="false"
            label="Filter by keyword"
            density="compact"
            variant="outlined"
            multiple
            clearable
            chips
            closable-chips
            hide-selected
            hide-details
            @update:model-value="(val) => updateSearchTerms((source) => (source.value = val))"
            @click:clear="updateSearchTerms((source) => (source.value = []))"
          >
            <template v-slot:no-data>
              <v-list-item>
                <v-list-item-title v-html="searchTermHint"></v-list-item-title>
              </v-list-item>
            </template>
          </v-combobox>

          <!-- SETTINGS MENU -->
          <div class="mt-1 ml-3">
            <v-menu :close-on-content-click="false" location="right bottom" offset="10">
              <template v-slot:activator="{ props: menu }">
                <v-tooltip location="top center">
                  <template v-slot:activator="{ props: tooltip }">
                    <v-icon v-bind="mergeProps(menu, tooltip)" :icon="mdiCog"></v-icon>
                  </template>
                  <span>Filter settings</span>
                </v-tooltip>
              </template>
              <v-card title="Filter settings" subtitle="Filter documents by search term where..." min-width="300">
                <v-card-text>
                  <!-- FILTER SETTINGS -->
                  <div class="mt-2 settings-grid">
                    <!-- CONTAINS -->
                    <div class="label">
                      <v-chip variant="tonal" color="#EE8434" label>
                        <v-icon :icon="mdiTextSearchVariant" start></v-icon>
                        Document contains...
                      </v-chip>
                    </div>
                    <div class="control">
                      <v-btn-toggle
                        v-model="searchTermSettings.documentContains"
                        variant="outlined"
                        density="compact"
                        mandatory
                      >
                        <v-btn value="every">
                          <span class="pr-1">All terms</span>
                          <v-icon v-if="searchTermSettings.documentContains == 'every'" :icon="mdiCheckBold"></v-icon>
                        </v-btn>
                        <v-btn value="some">
                          <span class="pr-1">Any terms</span>
                          <v-icon v-if="searchTermSettings.documentContains == 'some'" :icon="mdiCheckBold"></v-icon>
                        </v-btn>
                      </v-btn-toggle>
                    </div>

                    <!-- MATCH -->
                    <div class="label">
                      <v-chip variant="tonal" color="#C95D63" label>
                        <v-icon :icon="mdiShape" start></v-icon>
                        Text matches...
                      </v-chip>
                    </div>
                    <div class="control">
                      <v-btn-toggle
                        v-model="searchTermSettings.patternMatch"
                        variant="outlined"
                        density="compact"
                        mandatory
                        v-on:update:model-value="
                          (val) => updateSearchTermSettings((source) => (source.value['patternMatch'] = val))
                        "
                      >
                        <v-btn value="whole-word">
                          <span class="pr-1">Whole word</span>
                          <v-icon v-if="searchTermSettings.patternMatch == 'whole-word'" :icon="mdiCheckBold"></v-icon>
                        </v-btn>
                        <v-btn value="substring">
                          <span class="pr-1">Substring</span>
                          <v-icon v-if="searchTermSettings.patternMatch == 'substring'" :icon="mdiCheckBold"></v-icon>
                        </v-btn>
                      </v-btn-toggle>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-menu>
          </div>
        </div>

        <!-- ARRANGE MENUS -->
        <div class="d-flex align-center mt-4" style="column-gap: 12px">
          <!-- DOCUMENTS GROUP BY -->
          <v-select
            v-model="documentsGroupBy"
            :items="documentsGroupByValues"
            label="Group by"
            density="compact"
            variant="outlined"
            hide-details
            @update:model-value="(val) => (val == 'score' ? (nodesSortBy = 'score') : '')"
          >
          </v-select>

          <span>&rarr;</span>

          <!-- NODES SORT BY -->
          <v-select
            v-model="nodesSortBy"
            :items="nodesSortByValues"
            label="Sort by"
            density="compact"
            variant="outlined"
            hide-details
          >
          </v-select>
        </div>

        <!-- SIMILARITY SEARCH -->
        <div class="mt-4">
          <v-text-field
            v-model="documentsGroupByTask"
            :disabled="documentsGroupByTaskRunning"
            :loading="documentsGroupByTaskRunning"
            density="compact"
            label="Rank by similarity search"
            hint="Type a question, task, topic, etc."
            variant="outlined"
            persistent-hint
            @keydown.enter="documentsGroupByTask !== '' ? runDocumentsGroupByTask() : ''"
          >
            <template v-slot:append-inner>
              <v-btn
                :disabled="documentsGroupByTask == '' || documentsGroupByTaskRunning"
                :ripple="false"
                :icon="mdiPoll"
                density="compact"
                variant="plain"
                @click="runDocumentsGroupByTask"
              ></v-btn>
            </template>
          </v-text-field>
        </div>
      </div>
    </v-expand-transition>

    <v-divider class="my-2"></v-divider>

    <!-- DOCUMENTS LIST -->
    <div v-if="documents.length > 0 && nodes !== null" class="d-flex flex-column mx-1 doc-list-header">
      <div class="d-flex">
        <div class="flex-1-0">{{ documentsGroupByValues.find((x) => x.value == documentsGroupBy).title }}</div>
        <div>{{ nodesSortByValues.find((x) => x.value == nodesSortBy).title }}</div>
      </div>
    </div>
    <div class="overflow-auto px-3 mx-n3" style="padding-bottom: 0; margin-bottom: 12px">
      <template v-if="documents.length == 0">
        <div>No documents loaded.</div>
      </template>
      <template v-else-if="nodes == null">
        <div class="d-flex flex-wrap" style="gap: 12px">
          <span>No documents found containing the following search terms:</span>
          <v-chip v-for="term in searchTerms" label>
            <kbd>{{ term }}</kbd>
          </v-chip>
        </div>
      </template>
      <template v-else>
        <NestedList
          :nodes="nodes !== null && Object.hasOwn(nodes, 'children') ? nodes.children : nodes"
          :color="color"
          :nodes-sort-by="nodesSortBy"
          :search-terms="searchTerms"
          :search-term-pattern-match="searchTermSettings.patternMatch"
          :entity="entity"
          :update-node-selections="updateNodeSelections"
        />
      </template>
    </div>

    <!-- SELECT OPERATIONS -->
    <div class="d-flex flex-column">
      <div class="d-flex align-center">
        <v-icon :icon="mdiInformation"></v-icon>
        <div class="ml-1">{{ documentsFoundText }}</div>
      </div>
      <div v-if="someNodesSelected" class="d-flex mt-2" style="column-gap: 12px">
        <v-btn :prepend-icon="mdiPlusBoxMultipleOutline" @click="createPileFromSelectedNodes">Create Pile</v-btn>
        <v-btn :prepend-icon="mdiEraser" @click="clearSelectedNodes">Clear</v-btn>
      </div>
    </div>
  </v-col>
</template>

<script setup>
import { ref, toRaw, inject, computed, watch, mergeProps } from "vue";
import { stratify, interpolateRainbow } from "d3";
import { searchText, requestModel } from "@/utils";
import {
  mdiCog,
  mdiGraphOutline,
  mdiChartScatterPlot,
  mdiCheckBold,
  mdiShape,
  mdiTextSearchVariant,
  mdiPoll,
  mdiPlusBoxMultipleOutline,
  mdiEraser,
  mdiUnfoldMoreHorizontal,
  mdiUnfoldLessHorizontal,
  mdiInformation,
} from "@mdi/js";

import KnowledgeGraphDialog from "@/components/SourceView/KnowledgeGraphDialog.vue";
import EmbeddingsDialog from "@/components/SourceView/EmbeddingsDialog.vue";
import NestedList from "@/components/SourceView/NestedList.vue";

// define emitters
const emit = defineEmits(["requestCreatePileFromSelected"]);

// get providers
const { baseURL } = inject("baseURL");
const { documents, updateDocuments } = inject("documents");
const { searchTerms, updateSearchTerms, searchTermSettings, updateSearchTermSettings } = inject("searchTerms");
const { entity } = inject("entity");

// set ref
const nodes = ref([]); // files to display
const selectedNodes = ref({}); // whether a node is selected
const currentSearchTerm = ref(""); // current searched term
const showSearchSettings = ref(true);

const defaultDocumentsSortByValues = [
  { title: "Source", value: "source" },
  { title: "Date", value: "date" },
  { title: "Location", value: "location" },
  { title: "Topic", value: "topic" },
  { title: "Similarity", value: "score" },
];

const defaultNodesSortByValues = [
  { title: "Name", value: "name" },
  { title: "Title", value: "title" },
  { title: "Source", value: "source" },
  { title: "Date", value: "date" },
  { title: "Location", value: "location" },
  { title: "Topic", value: "topic" },
  { title: "Similarity", value: "score" },
];

const documentsGroupBy = ref("source");
const documentsGroupByValues = ref(defaultDocumentsSortByValues);

const nodesSortBy = ref("name");
const nodesSortByValues = ref(defaultNodesSortByValues);

const documentsGroupByTask = ref(""); // textfield string of task to group documents by
const documentsGroupByTaskRunning = ref(false); // whether current entity is being searched for
const documentTaskScoresUpdated = ref(0); // key to trigger refresh

// get data
let groups = Array.from(new Set(documents.value.map((d) => d[documentsGroupBy.value])));
let color = (group) => interpolateRainbow(groups.indexOf(group) / groups.length);

// update ref to trigger DOM update
selectedNodes.value = Object.fromEntries(documents.value.map((document) => [document.id, false]));
nodes.value = getNodeData();

// get computed
const documentsFoundText = computed(() => {
  let numFiles = null;
  let selectedMsg = ".";

  if (nodes.value == null) {
    numFiles = 0;
  } else if (nodes.value !== null && !Object.hasOwn(nodes.value, "children")) {
    numFiles = 1;
  } else {
    numFiles = nodes.value.leaves().length;
  }

  if (someNodesSelected.value) {
    const numSelected = Object.values(selectedNodes.value).filter((x) => x).length;
    selectedMsg = `; selected ${numSelected}.`;
  }

  return `Found ${numFiles} docs${selectedMsg}`;
});

const searchTermHint = computed(() => {
  if (currentSearchTerm.value === "") {
    return "Start typing a search term!";
  } else {
    return `Press <kbd>enter</kbd> to search for "${currentSearchTerm.value}"`;
  }
});

const someNodesSelected = computed(() => {
  return Object.values(selectedNodes.value).includes(true);
});

// when search terms change, search in node text for term
watch(
  [nodesSortBy, documentsGroupBy, documentTaskScoresUpdated, searchTerms, searchTermSettings, selectedNodes],
  () => {
    groups = Array.from(new Set(documents.value.map((d) => d[documentsGroupBy.value])));
    color = (group) => interpolateRainbow(groups.indexOf(group) / groups.length);
    nodes.value = getNodeData();
  },
  { deep: true }
);

/**
 * Get hierarchical list of nodes to populate nested list.
 *
 * Only include sources where every search term is found in text (AND)
 *
 * See: <https://observablehq.com/@d3/d3-stratify>
 */
function getNodeData() {
  let newNodes = null;

  // set node groups for d3 stratify path
  const docs = documents.value.map((d) => {
    let group = "";
    if (documentsGroupBy.value == "score") {
      group = d.name;
    } else if (documentsGroupBy.value == "date") {
      group = `${d[documentsGroupBy.value].replaceAll("/", "-")}/${d.name}`;
    } else {
      group = `${d[documentsGroupBy.value]}/${d.name}`;
    }
    return { ...d, group: group, selected: selectedNodes.value[d.id] };
  });

  // get new nodes
  if (searchTerms.value.length > 0) {
    const testTerm = (doc, term) => {
      return (
        searchText(doc.name, term, searchTermSettings.value.patternMatch) ||
        searchText(doc.text, term, searchTermSettings.value.patternMatch)
      );
    };
    const filteredDocs = docs.filter((d) => {
      switch (searchTermSettings.value.documentContains) {
        case "every":
          return searchTerms.value.every((term) => testTerm(d, term));
        case "some":
          return searchTerms.value.some((term) => testTerm(d, term));
      }
    });
    if (filteredDocs.length > 0) {
      newNodes = stratify().path((d) => d.group)(filteredDocs);
    }
  } else if (docs.length > 0) {
    newNodes = stratify().path((d) => d.group)(docs);
  }

  return newNodes;
}

/**
 * Searches for entity in KG
 */
function runDocumentsGroupByTask() {
  documentsGroupByTaskRunning.value = true; // disable typing

  // get request params
  const url = `${baseURL}/query`; // url to query backend server
  const body = {
    model_type: "openai", // type of transformer model that will perform the summarization
    model_checkpoint: null, // name of transformer model that will perform the summarization
    model_settings: {}, // user settings for model
    dataset: "live", // "practice" or "live" dataset
    task: "search_documents", // tells the server which prompts and routine to pick for calling LLM
    task_settings: { query: documentsGroupByTask.value, id_col: "source" }, // user settings for task
    documents: null, // list of strings, each considered a separate "document"
  };

  // make request
  requestModel(url, body)
    .then((data) => {
      if (data["success"] == true) {
        const documentScores = Object.fromEntries(data["texts"].map((x) => [x.id, x.score])); // get document scores
        const newDocuments = documents.value.map((document) => {
          return { ...document, score: documentScores[document.id] };
        });
        updateDocuments((source) => (source.value = newDocuments));
        nodesSortBy.value = "score";
        documentsGroupBy.value = "score";
        documentTaskScoresUpdated.value++; // trigger refresh
      } else {
        console.log(data["status"]);
        console.log(data["response"]);
      }
    })
    .catch((error) => {
      console.log(error);
    })
    .finally(() => {
      documentsGroupByTaskRunning.value = false; // enable typing
    });
}

function createPileFromSelectedNodes() {
  const newNodeList = documents.value.filter((document) => selectedNodes.value[document.id]);
  console.log(newNodeList);
  console.log(JSON.parse(JSON.stringify(newNodeList)));
  emit("requestCreatePileFromSelected", {
    nodeList: JSON.parse(JSON.stringify(newNodeList)), // create deep copy
  });
}

function updateNodeSelections(newNodeSelections) {
  const newSelectedNodes = structuredClone(toRaw(selectedNodes.value));
  newNodeSelections.forEach((node) => {
    newSelectedNodes[node.id] = node.select;
  });
  selectedNodes.value = newSelectedNodes;
}

function clearSelectedNodes() {
  selectedNodes.value = Object.fromEntries(documents.value.map((document) => [document.id, false]));
}
</script>

<style lang="scss">
.sources-title {
  font-family: "Teko", sans-serif;
  font-optical-sizing: auto;
  font-style: normal;
  font-weight: 700;
  font-size: 1.5rem;
  text-shadow: 1px 2px 2px black;
  color: white;
  height: 32px;
}

.settings-grid {
  display: grid;
  grid-template-columns: [col-1] auto [col-2] 1fr;
  row-gap: 6px;
  column-gap: 12px;

  .label {
    grid-column-start: col-1;
    display: flex;
    align-self: center;
    justify-content: end;
  }

  .control {
    grid-column-start: col-2;
    display: flex;
    align-self: center;
    justify-content: start;
  }
}

.doc-list-header {
  font-size: 0.9rem;
  opacity: 0.6;
}
</style>
