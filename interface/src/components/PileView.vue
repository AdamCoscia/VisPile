<template>
  <div class="d-flex flex-column overflow-hidden fill-height">
    <!-- HEADER -->
    <div class="pa-3 d-flex align-center justify-space-between">
      <!-- TITLE -->
      <header class="mx-5 piles-title">Piles</header>

      <!-- ACTIONS -->
      <div class="mr-5 d-flex align-center" style="gap: 12px">
        <!-- ENTITY -->
        <div class="d-flex flex-wrap align-center justify-end" style="gap: 12px">
          <!-- SEARCH -->
          <div style="width: 200px">
            <v-text-field
              v-model="entitySearch"
              :disabled="entitySearchRunning"
              :loading="entitySearchRunning"
              density="compact"
              label="Search entities"
              variant="outlined"
              hide-details
              single-line
              @keydown.enter="entitySearch !== '' ? runEntitySearch(entitySearch) : ''"
            >
              <template v-slot:append-inner>
                <v-btn
                  :disabled="entitySearch == '' || entitySearchRunning"
                  :ripple="false"
                  :icon="mdiMagnify"
                  density="compact"
                  variant="plain"
                  @click="runEntitySearch(entitySearch)"
                ></v-btn>
              </template>
            </v-text-field>
          </div>

          <!-- RESULT -->
          <div v-if="entity.name !== null" style="max-width: 200px">
            <div class="entity-name-label">{{ entity.name }}</div>
          </div>

          <!-- INSIGHTS -->
          <v-menu
            v-model="insightsMenuOpen"
            :disabled="entity.name == null || entitySearchRunning"
            :close-on-content-click="false"
            location="bottom right"
            offset="16"
          >
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                :disabled="entity.name == null || entitySearchRunning"
                :ripple="false"
                :icon="mdiLightbulb"
                density="compact"
                variant="plain"
              ></v-btn>
            </template>

            <v-card width="500">
              <!-- TITLE -->
              <v-card-item title="Knowledge Graph Insights">
                <template v-slot:prepend>
                  <v-icon :icon="mdiLightbulb"></v-icon>
                </template>
                <template v-slot:append>
                  <v-btn
                    :icon="mdiEraser"
                    variant="plain"
                    title="Clear entity"
                    @click="updateEntity((source) => (source.value.name = null))"
                  ></v-btn>
                </template>
              </v-card-item>

              <!-- BODY -->
              <v-card-text>
                <!-- FACTS -->
                <div class="fact-list">
                  <div class="fact-list-title">
                    Facts about
                    <span class="entity-label">{{ entity.name }}</span>
                  </div>
                  <v-list>
                    <v-list-item v-for="(fact, index) in entity.facts" :key="index">
                      <template v-slot:prepend>
                        <span class="mr-2">{{ index + 1 }}.</span>
                      </template>
                      <div class="fact-list-item" v-html="getFactHTML(fact)"></div>
                      <template v-slot:append>
                        <v-chip
                          density="comfortable"
                          title="Search for document"
                          label
                          @click="onInsightsDocumentClicked(nodeData[fact.document].name)"
                        >
                          {{ nodeData[fact.document].name }}
                        </v-chip>
                      </template>
                    </v-list-item>
                  </v-list>
                </div>

                <!-- RELATED ENTITIES -->
                <div class="related-entities">
                  <div class="mb-1 related-entities-title">Explore <b>connected</b> nodes:</div>
                  <div class="d-flex flex-wrap related-entities-list" style="gap: 6px 4px">
                    <v-chip
                      v-for="ent in entity.related"
                      class="related-entities-item"
                      density="compact"
                      variant="text"
                      title="Search for entity"
                      label
                      @click="runEntitySearch(ent)"
                    >
                      {{ ent }}
                    </v-chip>
                  </div>
                </div>

                <v-divider class="mt-6 mb-4"></v-divider>

                <!-- SIMILAR SEARCHES -->
                <div class="similar-entities">
                  <div class="mb-1 similar-entities-title">Did you mean:</div>
                  <div class="d-flex flex-wrap similar-entities-list" style="gap: 6px 4px">
                    <v-chip
                      v-for="ent in entity.similar"
                      class="similar-entities-item"
                      density="comfortable"
                      title="Search for entity"
                      label
                      @click="runEntitySearch(ent)"
                    >
                      {{ ent }}
                    </v-chip>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-menu>
        </div>

        <!-- SETTINGS -->
        <v-menu :close-on-content-click="false" location="left bottom" offset="10">
          <template v-slot:activator="{ props: menu }">
            <v-tooltip location="top center">
              <template v-slot:activator="{ props: tooltip }">
                <v-icon v-bind="mergeProps(menu, tooltip)" :icon="mdiCog"></v-icon>
              </template>
              <span>Pile settings</span>
            </v-tooltip>
          </template>
          <v-card title="Pile settings" subtitle="Filter piles" min-width="300">
            <v-card-text>
              <!-- FILTER -->
              <v-select
                v-model="selectedPiles"
                :items="piles"
                :disabled="piles.length == 0"
                label="Filter piles"
                density="compact"
                variant="outlined"
                item-title="name"
                multiple
                return-object
                hide-details
              >
                <template v-slot:prepend-item>
                  <v-list-item title="Select All" @click="togglePileSelectAll">
                    <template v-slot:prepend>
                      <v-checkbox-btn
                        :color="somePilesSelected ? '#4448ac' : undefined"
                        :indeterminate="somePilesSelected && !allPilesSelected"
                        :model-value="allPilesSelected"
                      ></v-checkbox-btn>
                    </template>
                  </v-list-item>
                  <v-divider class="mt-2"></v-divider>
                </template>
                <template v-slot:selection="{ item, index }">
                  <span v-if="index < 1">
                    {{ item.title }}
                  </span>
                  <span v-if="index === 1" class="text-grey text-caption align-self-center">
                    (+{{ selectedPiles.length - 1 }})
                  </span>
                </template>
              </v-select>
            </v-card-text>
          </v-card>
        </v-menu>
      </div>
    </div>

    <v-divider class="mx-4 mb-2"></v-divider>

    <!-- RESULTS -->
    <div class="pa-1 d-flex flex-wrap overflow-auto">
      <!-- CURRENT PILE -->
      <Pile
        v-for="pile in selectedPiles"
        :key="pile.id"
        :pile="pile"
        :enable-pile-edit-name="enablePileEditName"
        :bookmark-pile="bookmarkPile"
        :clone-pile="clonePile"
        :remove-pile="removePile"
        :update-pile-name="updatePileName"
        :toggle-pile-response-visible="togglePileResponseVisible"
        :run-entity-search="runEntitySearch"
        :run-pile-task-query="runPileTaskQuery"
        :get-pile-entities="getPileEntities"
        :clear-pile-entities="clearPileEntities"
        :get-pile-links="getPileLinks"
        :clear-pile-links="clearPileLinks"
        :select-linked-sentences="selectLinkedSentences"
        :clear-linked-sentences="clearLinkedSentences"
        :run-pile-search-documents-query="runPileSearchDocumentsQuery"
        :get-pile-document-topics="getPileDocumentTopics"
        :validate-change-pile-node="validateChangePileNode"
        :set-pile-active-node="setPileActiveNode"
        :remove-pile-node="removePileNode"
      ></Pile>

      <!-- NEW PILE -->
      <v-col cols="4" class="pt-6" style="min-width: 160px">
        <v-card elevation="3" class="fill-height" style="min-height: 72px">
          <div class="d-flex align-center justify-center fill-height">
            <v-btn @click="() => createPile()">New pile</v-btn>
          </div>
        </v-card>
      </v-col>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, computed, watch, toRaw, nextTick, mergeProps } from "vue";
import * as d3 from "d3";
import lda from "@/utils/lda";
import {
  requestModel,
  formatNumber,
  removeExtraNewlines,
  highlightText,
  getCopyName,
  escapeHTML,
  getRandomSample,
} from "@/utils";
import { mdiMagnify, mdiLightbulb, mdiEraser, mdiCog } from "@mdi/js";

import Pile from "@/components/PileView/Pile.vue";

// define expose
defineExpose({ createPile }); // these are available in parent Page.vue

// define emitters
const emit = defineEmits(["requestCreateBookmarkFromPile"]);

// get providers
const { baseURL } = inject("baseURL");
const { documents } = inject("documents");
const { searchTerms, updateSearchTerms, searchTermSettings } = inject("searchTerms");
const { piles, updatePiles } = inject("piles");
const { entity, updateEntity } = inject("entity");
const { models } = inject("models");
const { knowledgeGraph } = inject("knowledgeGraph");

// set refs
const pileId = ref(0); // continously incrementing unique piling id
const nodeData = ref({}); // node data look up
const selectedPiles = ref([]); // only selected piles

const insightsMenuOpen = ref(false); // to open/close insights menu
const entitySearch = ref(""); // textfield string of entity to search for in KG
const entitySearchRunning = ref(false); // whether current entity is being searched for

const togglePileSelectAll = () => (selectedPiles.value = allPilesSelected.value ? [] : piles.value.slice());

// get node data
nodeData.value = Object.fromEntries(
  documents.value.map((d) => {
    return [d.id, d];
  })
);

// create first pile automatically
createPile();

// get computed
const allPilesSelected = computed(() => {
  return piles.value.length == selectedPiles.value.length;
});
const somePilesSelected = computed(() => {
  return selectedPiles.value.length > 0;
});

// when search terms change, update response and node HTML in all piles
watch(
  [searchTerms, searchTermSettings, entity],
  () => {
    piles.value.forEach((pile) => updatePileHTML(pile.id));
  },
  { deep: true }
);

/**
 * Add new pile, adding/overwriting any properties from `pileOpts`.
 */
function createPile(pileOpts = {}) {
  const ts = new Date(Date.now());
  const defaultPile = {
    id: pileId.value,
    name: `Pile ${pileId.value + 1}`,
    createdAt: ts,
    updateHistory: [],
    selected: true,
    editNameEnabled: false,
    model: structuredClone(toRaw(models.value[0])),
    models: models.value.map((x) => structuredClone(toRaw(x))),
    queryRunning: false,
    responseText: null,
    responseTextHTML: null,
    responseStats: null,
    showResponse: true,
    isResponseMonospace: false,
    entities: [],
    linkedSentences: [],
    selectedLinkedSentences: [],
    documentTopics: [],
    nodeList: [],
    activeNode: null,
    activeNodeHTML: null,
  };
  const newPile = {
    ...defaultPile,
    ...pileOpts, // overwrites properties with the same key
  };
  newPile.updateHistory.push({ event: "createPile", ts: ts });
  updatePiles((source) => source.value.push(newPile));
  selectedPiles.value.push(newPile);
  pileId.value++;
}

/**
 * Clone pile at `pileIndex`.
 */
function clonePile(pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  const pile = piles.value[pileIndex];
  const copyName = pile.name.slice() + " - Copy";
  const newName = getCopyName(
    piles.value.map((x) => x.name),
    copyName
  );
  createPile({
    name: newName,
    nodeList: structuredClone(pile.nodeList.map((node) => toRaw(node))), // create deep copy
  });
}

/**
 * Remove pile at `pileIndex`.
 */
function removePile(pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  updatePiles((source) => source.value.splice(pileIndex, 1));
  const selectedPileIndex = selectedPiles.value.findIndex((pile) => pile.id == pileId);
  selectedPiles.value.splice(selectedPileIndex, 1);
}

/**
 * Set pile into edit name mode and focus input element automatically.
 */
function enablePileEditName(pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  updatePiles((source) => (source.value[pileIndex].editNameEnabled = true));
  nextTick(() => {
    document.querySelector(`input[name="PileName${pileId}"]`).focus();
  });
}

/**
 * Update pile name when pile title input field changes.
 */
function updatePileName(newPileName, pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  if (newPileName !== "") updatePiles((source) => (source.value[pileIndex].name = newPileName));
  updatePiles((source) => (source.value[pileIndex].editNameEnabled = false));
  updatePiles((source) =>
    source.value[pileIndex].updateHistory.push({
      event: "updatePileName",
      ts: new Date(Date.now()),
    })
  );
}

/**
 * Add/remove pile as a bookmark.
 */
function bookmarkPile(pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  const pile = piles.value[pileIndex];
  emit("requestCreateBookmarkFromPile", {
    name: `"${pile.name}" bookmark`,
    responseText: pile.responseText.slice(),
    responseTextHTML: pile.responseTextHTML.slice(),
    entities: structuredClone(pile.entities.map((ent) => toRaw(ent))), // create deep copy
    nodeList: structuredClone(pile.nodeList.map((node) => toRaw(node))), // create deep copy
  });
}

/**
 * Searches for entity in KG
 */
function runEntitySearch(term, fromTextClick = false) {
  insightsMenuOpen.value = false; // close insights menu
  entitySearchRunning.value = true; // disable search

  // if called by clicking on term highlighted in text, put term in search text field
  if (fromTextClick) entitySearch.value = term;

  // get request pararms
  const url = `${baseURL}/query`; // url to query backend server
  const body = {
    model_type: "openai", // type of transformer model that will perform the summarization
    model_checkpoint: null, // name of transformer model that will perform the summarization
    model_settings: {}, // user settings for model
    dataset: "live", // "practice" or "live" dataset
    task: "search_nodes", // tells the server which prompts and routine to pick for calling LLM
    task_settings: { query: term, top_n: 6, id_col: "node" }, // user settings for task
    documents: null, // list of strings, each considered a separate "document"
  };

  // make request
  requestModel(url, body)
    .then((data) => {
      if (data["success"] == true) {
        const foundEntities = data["texts"]; // get entities
        const newEntity = foundEntities[0].id; // get top response as new entity
        const newSimilar = foundEntities.slice(1, 6).map((ent) => ent.id); // get up to 5 similar entities from search

        // find nodes and links in KG related to search
        const allFacts = knowledgeGraph.value.links
          .slice()
          .filter((link) => link.source == newEntity || link.target == newEntity);
        const allEntities = allFacts.flatMap((link) => [link.source, link.target]).filter((ent) => ent !== newEntity);
        const uniqueEntities = [...new Set(allEntities)];
        const allRelatedEntitiesSorted = uniqueEntities
          .map((ent) => knowledgeGraph.value.nodes.find((node) => node.id == ent))
          .sort((a, b) => (a.degree > b.degree ? -1 : 1));

        // sample facts and related nodes
        const nSamples = Math.min(allFacts.length, 5);
        const newFacts = getRandomSample(allFacts, nSamples); // randomly sample up to 5 facts
        const newRelated = allRelatedEntitiesSorted.slice(0, 5).map((node) => node.id); // get up to 5 related nodes

        // save values
        updateEntity((source) => (source.value.name = newEntity));
        updateEntity((source) => (source.value.facts = newFacts));
        updateEntity((source) => (source.value.related = newRelated));
        updateEntity((source) => (source.value.similar = newSimilar));

        // enable
        insightsMenuOpen.value = true; // open insights menu
      } else {
        console.log(data["status"]);
        console.log(data["response"]);
      }
    })
    .catch((error) => {
      console.log(error);
    })
    .finally(() => {
      entitySearchRunning.value = false; // enable search
    });
}

/**
 * Returns formatted HTML for a fact in insights menu.
 */
function getFactHTML(fact) {
  const sourceFontStyle = fact.source == entity.value.name ? 'style="font-weight: 700"' : "";
  const targetFontStyle = fact.target == entity.value.name ? 'style="font-weight: 700"' : "";
  const items = [
    `<span ${sourceFontStyle}>${escapeHTML(fact.source)}</span>`,
    `<span>${escapeHTML(fact.label)}</span>`,
    `<span ${targetFontStyle}>${escapeHTML(fact.target)}</span>`,
  ];
  return items.join(" &#8594; ");
}

/**
 * Add document to search when clicked in insights menu.
 */
function onInsightsDocumentClicked(term) {
  if (!searchTerms.value.includes(term)) updateSearchTerms((source) => source.value.push(term));
}

/**
 * Creates, executes and processes query to requested pile task.
 */
function runPileTaskQuery(pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  const pile = piles.value[pileIndex];
  const documents = pile.nodeList.map((node) => removeExtraNewlines(nodeData.value[node.id].text));
  if (documents.length > 0) {
    // prepare pile
    clearPileResponse(pileIndex); // clear response text and stats
    updatePiles((source) => (source.value[pileIndex].queryRunning = true)); // disable query controls for this pile

    // get request params
    const url = `${baseURL}/query`; // url to query backend server
    const body = {
      model_type: pile.model.type, // type of transformer model that will perform the task
      model_checkpoint: pile.model.value, // name of transformer model that will perform the task
      model_settings: pile.model.settings, // user settings for model
      dataset: "live", // "practice" or "live" dataset
      task: pile.model.task.value, // tells the server which prompts and routine to pick for calling LLM
      task_settings: pile.model.task.settings, // user settings for task
      documents: documents, // list of strings, each considered a separate "document"
    };

    // make request
    requestModel(url, body)
      .then((data) => {
        const text = data["text"]; // get response text
        const stats = Object.hasOwn(data, "stats") ? formatStats(data["stats"]) : null; // get response stats
        updatePiles((source) => (source.value[pileIndex].responseText = text));
        updatePiles((source) => (source.value[pileIndex].responseStats = stats));
        updatePileHTML(pileId); // update pile HTML
      })
      .catch((error) => {
        console.log(error);
        updatePiles((source) => (source.value[pileIndex].responseText = "Query failed; check console."));
        updatePiles((source) => (source.value[pileIndex].responseTextHTML = "Query failed; check console."));
        updatePiles((source) => (source.value[pileIndex].responseStats = null));
      })
      .finally(() => {
        updatePiles((source) => (source.value[pileIndex].queryRunning = false)); // enable query controls for this pile
        updatePiles((source) =>
          source.value[pileIndex].updateHistory.push({
            event: "updatePileResponse",
            ts: new Date(Date.now()),
          })
        );
      });
  }
}

/**
 * Formats model response statistics and returns them in a list.
 */
function formatStats(stats) {
  const statsList = [];

  if (Object.hasOwn(stats, "status")) {
    statsList.push({
      title: "Server Response Status",
      value: stats["status"],
      color: "white",
      background: "#C95D63",
    });
  }

  if (Object.hasOwn(stats, "rouge1")) {
    statsList.push({
      title: "Unigrams",
      value: formatNumber(stats["rouge1"], 2),
      color: "white",
      background: "#048A81",
    });
  }

  if (Object.hasOwn(stats, "rouge2")) {
    statsList.push({
      title: "Bigrams",
      value: formatNumber(stats["rouge2"], 2),
      color: "white",
      background: "#048A81",
    });
  }

  if (Object.hasOwn(stats, "rougeL")) {
    statsList.push({
      title: "Sequences",
      value: formatNumber(stats["rougeL"], 2),
      color: "white",
      background: "#048A81",
    });
  }

  if (Object.hasOwn(stats, "percent_reduction")) {
    const output = stats["percent_reduction"].output;
    const input = stats["percent_reduction"].input;
    const value = formatNumber(stats["percent_reduction"].value, 2);
    statsList.push({
      title: "Reduction",
      value: `${output} / ${input} (${value}%)`,
      color: "white",
      background: "#048A81",
    });
  }

  return statsList;
}

/**
 * Toggles visibility of pile response.
 */
function togglePileResponseVisible(pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  updatePiles((source) => (source.value[pileIndex].showResponse = !source.value[pileIndex].showResponse));
}

/**
 * Get list of entities from response text that match nodes in the KG.
 */
function getPileEntities(pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  const pile = piles.value[pileIndex];
  const text = pile.responseText.toLowerCase();
  const entities = [];
  knowledgeGraph.value.nodes.forEach((node) => {
    if (text.includes(node.id.toLowerCase())) {
      entities.push(node.id);
    }
  });
  updatePiles((source) => (source.value[pileIndex].entities = entities)); // save extracted entities
  updatePileHTML(pileId); // update pile HTML
}

/**
 * Clear list of entities from pile and update pile response HTML.
 */
function clearPileEntities(pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  updatePiles((source) => (source.value[pileIndex].entities = []));
  updatePileHTML(pileId); // update pile HTML
}

/**
 * Get links between sentences in pile response text and document nodes.
 */
function getPileLinks(pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  const pile = piles.value[pileIndex];
  const documents = pile.nodeList.map((node) => {
    return { id: node.id, text: removeExtraNewlines(nodeData.value[node.id].text) };
  });
  if (documents.length > 0) {
    // prepare pile
    updatePiles((source) => (source.value[pileIndex].queryRunning = true)); // disable query controls for this pile

    // get request params
    const url = `${baseURL}/query`; // url to query backend server
    const body = {
      model_type: "openai", // type of transformer model that will perform the summarization
      model_checkpoint: null, // name of transformer model that will perform the summarization
      model_settings: {}, // user settings for model
      dataset: "live", // "practice" or "live" dataset
      task: "compare_sentences", // tells the server which prompts and routine to pick for calling LLM
      task_settings: { query: { id: pile.id, text: pile.responseText }, top_n: 1 }, // user settings for task
      documents: documents, // list of strings, each considered a separate "document"
    };

    // make request
    requestModel(url, body)
      .then((data) => {
        if (data["success"] == true) {
          const newLinkedSentences = data["links"];
          updatePiles((source) => (source.value[pileIndex].linkedSentences = newLinkedSentences));
          updatePileHTML(pileId); // update pile HTML
        } else {
          console.log(data["status"]);
          console.log(data["response"]);
        }
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        updatePiles((source) => (source.value[pileIndex].queryRunning = false)); // enable query controls for this pile
      });
  }
}

/**
 * Clear list of linked sentences from pile and update pile response HTML.
 */
function clearPileLinks(pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  updatePiles((source) => (source.value[pileIndex].linkedSentences = []));
  updatePiles((source) => (source.value[pileIndex].selectedLinkedSentences = []));
  updatePileHTML(pileId); // update pile HTML
}

/**
 * Sets selected linked sentences on click.
 */
function selectLinkedSentences(linkIndices, pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  const pile = piles.value[pileIndex];
  const newLinkedSentences = linkIndices.map((linkIndex) => {
    return { link: pile.linkedSentences[linkIndex], index: linkIndex };
  });
  updatePiles((source) => (source.value[pileIndex].selectedLinkedSentences = newLinkedSentences));
  updatePileHTML(pileId); // update pile HTML
}

/**
 * Clear selected linked sentences when click on an already selected sentence.
 */
function clearLinkedSentences(pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  updatePiles((source) => (source.value[pileIndex].selectedLinkedSentences = []));
  updatePileHTML(pileId); // update pile HTML
}

/**
 * Remove pile response text, scores, entities and linked sentences.
 */
function clearPileResponse(pileIndex) {
  const pile = piles.value[pileIndex];
  updatePiles((source) => (source.value[pileIndex].responseText = null)); // remove previous response text
  updatePiles((source) => (source.value[pileIndex].responseTextHTML = null)); // remove previous response text HTML
  updatePiles((source) => (source.value[pileIndex].responseStats = null)); // remove previous response stats
  updatePiles((source) => (source.value[pileIndex].entities = [])); // clear entities
  updatePiles((source) => (source.value[pileIndex].linkedSentences = [])); // clear linked sentences
  updatePiles((source) => (source.value[pileIndex].selectedLinkedSentences = [])); // clear selected sentences
  updatePileHTML(pile.id); // update pile HTML
}

/**
 * Creates, executes and processes query to search for documents related to the pile response.
 */
function runPileSearchDocumentsQuery(pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  const pile = piles.value[pileIndex];

  // prepare pile
  updatePiles((source) => (source.value[pileIndex].queryRunning = true)); // disable query controls for this pile

  // get request params
  const url = `${baseURL}/query`; // url to query backend server
  const body = {
    model_type: "openai", // type of transformer model that will perform the summarization
    model_checkpoint: null, // name of transformer model that will perform the summarization
    model_settings: {}, // user settings for model
    dataset: "live", // "practice" or "live" dataset
    task: "search_documents", // tells the server which prompts and routine to pick for calling LLM
    task_settings: { query: pile.responseText, top_n: 5, id_col: "source" }, // user settings for task
    documents: null, // list of strings, each considered a separate "document"
  };

  // make request
  requestModel(url, body)
    .then((data) => {
      if (data["success"] == true) {
        const newDocuments = data["texts"]; // get documents
        newDocuments.forEach((document) => addPileNode(document.id, pileId)); // add document to nodeList
      } else {
        console.log(data["status"]);
        console.log(data["response"]);
      }
    })
    .catch((error) => {
      console.log(error);
    })
    .finally(() => {
      updatePiles((source) => (source.value[pileIndex].queryRunning = false)); // enable query controls for this pile
      updatePiles((source) =>
        source.value[pileIndex].updateHistory.push({
          event: "updatePileNodes",
          ts: new Date(Date.now()),
        })
      );
    });
}

/**
 * Perform topic modeling to get topics of documents in pile.
 */
function getPileDocumentTopics(pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  const pile = piles.value[pileIndex];
  let newDocumentTopics = ["..."];
  const documents = pile.nodeList.map((node) => removeExtraNewlines(nodeData.value[node.id].text));
  if (documents.length > 0) {
    const result = lda(documents, 1, 5, ["en_las2024"]); // perform LDA, get top 5 keywords for 1 topic
    newDocumentTopics = result[0].map((d) => d.term);
  }
  updatePiles((source) => (source.value[pileIndex].documentTopics = newDocumentTopics)); // store in pile object
  return newDocumentTopics;
}

/**
 * Add node to pile, if node doesn't exist in node list already.
 */
function addPileNode(nodeId, pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  const pile = piles.value[pileIndex];
  const nodeExists = pile.nodeList.some((node) => node.id == nodeId);
  if (!nodeExists) {
    const node = nodeData.value[nodeId]; // get node data
    node.isNew = true; // add property to node
    clearPileLinks(pileId); // since new nodes are added, we want to remove old links
    updatePiles((source) => source.value[pileIndex].nodeList.push(node));
    updatePiles((source) =>
      source.value[pileIndex].updateHistory.push({
        event: "addPileNode",
        ts: new Date(Date.now()),
      })
    );
  }
}

/**
 * Perform actions when draggable pile changes:
 * 1. prevent duplicates when adding to a pile.
 * 2. reset response text when adding to / removing from a pile.
 *
 * `evt` is emitted by draggable
 * - See: <https://github.com/SortableJS/vue.draggable.next#events>
 */
function validateChangePileNode(evt, pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  const pile = piles.value[pileIndex];
  const pileNodeList = pile.nodeList;
  if (Object.hasOwn(evt, "added")) {
    if (pileNodeList.filter((d) => d.id == evt.added.element.id).length > 1) {
      // remove element added if duplicates exist in the pile
      updatePiles((source) => source.value[pileIndex].nodeList.splice(evt.added.newIndex, 1));
    } else {
      // new node added, reset response when pile changes
      clearPileResponse(pileIndex);
      updatePiles((source) =>
        source.value[pileIndex].updateHistory.push({
          event: "addPileNode",
          ts: new Date(Date.now()),
        })
      );
    }
  }
}

/**
 * Remove node from pile.
 */
function removePileNode(node, pileNodeIndex, pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  const pile = piles.value[pileIndex];
  updatePiles((source) => source.value[pileIndex].nodeList.splice(pileNodeIndex, 1));
  const prevActiveNode = pile.activeNode;
  if (prevActiveNode !== null && prevActiveNode.id == node.id) {
    updatePiles((source) => (source.value[pileIndex].activeNode = null));
  }
  clearPileResponse(pileIndex); // reset response when pile changes
  updatePiles((source) =>
    source.value[pileIndex].updateHistory.push({
      event: "removePileNode",
      ts: new Date(Date.now()),
    })
  );
}

/**
 * Set new pile active node and show node text in callout box.
 */
function setPileActiveNode(node, pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  const pile = piles.value[pileIndex];
  let newActiveNode = nodeData.value[node.id];
  const prevActiveNode = pile.activeNode;
  if (prevActiveNode !== null && prevActiveNode.id == node.id) {
    // if node clicked is same as old, unset
    newActiveNode = null;
  } else {
    // is node clicked is new, update!
    updatePiles((source) => {
      const nodeIndex = source.value[pileIndex].nodeList.findIndex((node) => node.id == newActiveNode.id);
      source.value[pileIndex].nodeList[nodeIndex].isNew = false; // node is no longer new (has been clicked on)
    }); // update node list
    updatePiles((source) => (source.value[pileIndex].activeNodeHTML = getActiveNodeHTML(newActiveNode, pile))); // update pile node text
    makeNestedTermsHoverable();
  }
  updatePiles((source) => (source.value[pileIndex].activeNode = newActiveNode));
}

/**
 * Update all HTML in `pileId`.
 */
function updatePileHTML(pileId) {
  const pileIndex = piles.value.findIndex((pile) => pile.id == pileId);
  const pile = piles.value[pileIndex];
  if (pile.responseText !== null) {
    updatePiles((source) => (source.value[pileIndex].responseTextHTML = getResponseTextHTML(pile)));
  }
  if (pile.activeNode !== null) {
    updatePiles((source) => (source.value[pileIndex].activeNodeHTML = getActiveNodeHTML(pile.activeNode, pile)));
  }
  makeNestedTermsHoverable();
}

/**
 * Returns formatted HTML response `text` that isolates terms (search, entity, extracted, links) as their own spans.
 */
function getResponseTextHTML(pile) {
  const clean = escapeHTML(pile.responseText);
  const terms = [];
  // search terms
  if (searchTerms.value.length > 0) {
    terms.push(
      ...searchTerms.value.map((term) => {
        return {
          text: escapeHTML(term),
          termClassName: "search-term",
          patternType: searchTermSettings.value.patternMatch,
        };
      })
    );
  }
  // extracted
  if (pile.entities.length > 0) {
    terms.push(
      ...pile.entities.map((term) => {
        return { text: escapeHTML(term), termClassName: "extracted-term", patternType: "whole-word" };
      })
    );
  }
  // searched entity
  if (entity.value.name !== null) {
    terms.push({ text: escapeHTML(entity.value.name), termClassName: "entity-term", patternType: "whole-word" });
  }
  // links
  terms.push(...createLinkedSentencesHTMLHighlightTerms(pile, "query"));
  const html = highlightText(clean, terms);
  return html;
}

/**
 * Returns cleaned and formatted HTML node `text` that isolates terms (search, entity, links) as their own spans.
 */
function getActiveNodeHTML(node, pile) {
  const clean = escapeHTML(removeExtraNewlines(node.text));
  const terms = [];
  // search terms
  if (searchTerms.value.length > 0) {
    terms.push(
      ...searchTerms.value.map((term) => {
        return {
          text: escapeHTML(term),
          termClassName: "search-term",
          patternType: searchTermSettings.value.patternMatch,
        };
      })
    );
  }
  // searched entity
  if (entity.value.name !== null) {
    terms.push({ text: escapeHTML(entity.value.name), termClassName: "entity-term", patternType: "whole-word" });
  }
  // links
  terms.push(...createLinkedSentencesHTMLHighlightTerms(pile, "document", node));
  const html = highlightText(clean, terms);
  return html;
}

/**
 * Makes it so that only the innermost nested span has the hover state applied.
 *
 * See: <https://stackoverflow.com/a/31612543>
 */
function makeNestedTermsHoverable() {
  nextTick(() => {
    d3.selectAll(".search-term, .extracted-term, .entity-term, .linked-sentence")
      .on("mouseover", function (e) {
        d3.select(this).classed("hovering", e.type === "mouseover");
        e.stopPropagation();
      })
      .on("mouseout", function (e) {
        d3.select(this).classed("hovering", e.type === "mouseover");
        e.stopPropagation();
      });
  });
}

/**
 * Helper function to create terms that can be passed to `highlightText`.
 */
function createLinkedSentencesHTMLHighlightTerms(pile, source, activeNode = null) {
  const terms = [];
  const documentIds = pile.nodeList.map((node) => node.id);
  const colorLink = d3.scaleOrdinal(documentIds, d3.schemeCategory10);

  let sentenceSourceKey = "";
  let sourceSentenceIndex = "";
  switch (source) {
    case "query": {
      sentenceSourceKey = "query_sent";
      sourceSentenceIndex = "query_sent_index";
      break;
    }
    case "document": {
      sentenceSourceKey = "document_sent";
      sourceSentenceIndex = "document_sent_index";
      break;
    }
  }

  // create term from linked sentence
  const createTermFromLink = (link, opacity, selected) => {
    const sentence = link[sentenceSourceKey]; // sentence to search
    const documentId = link["document_id"]; // document that sentence is linked to
    const hex = colorLink(documentId); // get color hex of link
    const rgb = hex
      .replace(/^#?([a-f\d])([a-f\d])([a-f\d])$/i, (m, r, g, b) => "#" + r + r + g + g + b + b)
      .substring(1)
      .match(/.{2}/g)
      .map((x) => parseInt(x, 16)); // convert hex to rgb
    return {
      text: escapeHTML(sentence),
      termClassName: "linked-sentence",
      patternType: "substring",
      selected: selected,
      linkIndices: [link["query_sent_index"]],
      linkColor: `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${opacity})`,
    };
  };

  const linkedSentenceTerms = {};
  let linkOpacity = 1;
  let selectedLinkIndices = [];

  // create term for selected linked sentence, if exists
  if (pile.selectedLinkedSentences.length > 0) {
    const filteredLinks = pile.selectedLinkedSentences.filter(
      (selectedLink) =>
        source !== "document" || (source == "document" && selectedLink.link["document_id"] == activeNode.id)
    );
    filteredLinks.forEach((selectedLink) => {
      const link = selectedLink.link;
      const sentIndex = link[sourceSentenceIndex]; // index of source sentence
      if (Object.hasOwn(linkedSentenceTerms, sentIndex)) {
        // there is a query sentence with the same document sentence linked
        linkedSentenceTerms[sentIndex].linkIndices.push(link["query_sent_index"]);
      } else {
        // this is the first query/source sentence pair for this link's source sentence
        linkedSentenceTerms[sentIndex] = createTermFromLink(link, linkOpacity, true);
      }
    });
    linkOpacity = 0.4; // make all other links faded when there are selected links
    selectedLinkIndices = filteredLinks.map((link) => link.index); // don't redraw selected links
  }

  // create terms for all linked sentences, without duplicating selected sentence
  if (pile.linkedSentences.length > 0) {
    const filteredLinks = pile.linkedSentences.filter(
      (link) => source !== "document" || (source == "document" && link["document_id"] == activeNode.id)
    );
    filteredLinks.forEach((link, index) => {
      if (!selectedLinkIndices.includes(index)) {
        const sentIndex = link[sourceSentenceIndex]; // index of source sentence
        if (Object.hasOwn(linkedSentenceTerms, sentIndex)) {
          // there is a query sentence with the same document sentence linked
          linkedSentenceTerms[sentIndex].linkIndices.push(link["query_sent_index"]);
        } else {
          // this is the first query/source sentence pair for this link's source sentence
          linkedSentenceTerms[sentIndex] = createTermFromLink(link, linkOpacity, false);
        }
      }
    });
  }

  // flatten terms into list
  terms.push(...Object.values(linkedSentenceTerms));

  return terms;
}
</script>

<style lang="scss">
.piles-title {
  padding-top: 4px;
  font-family: "Teko", sans-serif;
  font-optical-sizing: auto;
  font-style: normal;
  font-weight: 700;
  font-size: 2rem;
  line-height: 36px;
  height: 36px;
  color: #262626;
}

.entity-name-label {
  padding: 4px 6px;
  font-size: 0.9rem;
  line-height: 1rem;
  font-weight: 700;
  background-color: rgb(68, 72, 172, 0.12);
  color: rgb(68, 72, 172);
  border-radius: 4px;
  word-break: break-word;
}

.fact-list {
  .fact-list-title {
    font-size: 1.1rem;
    font-weight: 700;
    line-height: 1.5rem;

    .entity-label {
      padding: 4px 6px;
      font-size: 0.8rem;
      font-weight: 700;
      background-color: rgb(68, 72, 172, 0.12);
      color: rgb(68, 72, 172);
      border-radius: 4px;
      word-break: break-word;
    }
  }

  .fact-list-item {
    padding-right: 12px;
    font-size: 0.9rem;
  }
}

.related-entities {
  padding-left: 8px;
  border-left: 4px solid #ccc;

  .related-entities-title {
    font-size: 0.9rem;
    opacity: 0.6;
  }

  .related-entities-item {
    padding: 4px 6px;
    font-size: 0.8rem;
    font-weight: 700;
    background-color: rgb(68, 72, 172, 0.12);
    color: rgb(68, 72, 172);
    border-radius: 4px;
    word-break: break-word;
  }
}

.similar-entities {
  .similar-entities-title {
    font-size: 0.9rem;
    font-style: italic;
    line-height: 1rem;
  }

  .similar-entities-list {
    .v-chip {
      height: auto !important;
      padding: 4px 6px;
    }

    .v-chip__content {
      max-width: 100%;
      height: auto;
      white-space: pre-wrap;
      word-break: break-word;
      font-weight: 700;
      font-size: 0.75rem;
      line-height: 0.75rem;
    }
  }
}
</style>
