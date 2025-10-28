<template>
  <v-col :cols="getPileCols()" class="pt-5" style="min-width: 300px">
    <!-- PILE CONTROLS -->
    <div class="pile-controls-floating-wrapper">
      <v-card class="d-flex justify-end">
        <v-icon
          :color="pile.editNameEnabled ? 'primary' : ''"
          :icon="pile.editNameEnabled ? mdiPencil : mdiPencilOutline"
          density="comfortable"
          title="Edit pile name"
          @click="pile.editNameEnabled ? savePileNameField(pile.id) : enablePileEditName(pile.id)"
        ></v-icon>
        <v-icon :icon="mdiContentCopy" density="comfortable" @click="clonePile(pile.id)" title="Copy pile"></v-icon>
        <v-icon :icon="mdiClose" density="comfortable" @click="removePile(pile.id)" title="Remove pile"></v-icon>
      </v-card>
    </div>

    <!-- PILE CONTENTS -->
    <v-card elevation="3">
      <!-- PILE TITLE -->
      <v-card-item>
        <v-card-title>
          <div class="d-flex align-center pile-title-wrapper">
            <template v-if="pile.editNameEnabled">
              <input
                :name="'PileName' + pile.id"
                :placeholder="pile.name"
                :value="pile.name"
                type="text"
                style="width: 100%"
              />
            </template>
            <template v-else>
              <span>{{ pile.name }}</span>
            </template>
          </div>
        </v-card-title>
        <template v-if="pile.nodeList.length > 0">
          <v-card-subtitle>Last updated: {{ pile.updateHistory.at(-1).ts.toLocaleString() }}</v-card-subtitle>
        </template>
      </v-card-item>

      <template v-if="pile.nodeList.length > 0">
        <!-- PILE OPERATIONS -->
        <v-col class="pt-0">
          <!-- PILE QUERY -->
          <v-row>
            <PileQuery
              :pile="pile"
              :run-pile-query="runPileTaskQuery"
              :toggle-pile-response-visible="togglePileResponseVisible"
            />
          </v-row>

          <!-- PILE RESPONSE AND STATS -->
          <v-expand-transition>
            <v-row v-if="pile.showResponse && pile.responseText !== null">
              <v-col class="pile-response-wrapper">
                <!-- PILE RESPONSE -->
                <div>
                  <div class="mb-1 d-flex align-center" style="gap: 12px">
                    <div class="section-label">Response:</div>
                    <v-btn
                      v-if="pile.entities.length > 0"
                      :prepend-icon="mdiEraser"
                      size="small"
                      density="comfortable"
                      variant="tonal"
                      @click="clearPileEntities(pile.id)"
                    >
                      Clear extracted
                    </v-btn>
                    <v-btn
                      v-if="pile.linkedSentences.length > 0"
                      :prepend-icon="mdiEraser"
                      size="small"
                      density="comfortable"
                      variant="tonal"
                      @click="clearPileLinks(pile.id)"
                    >
                      Clear links
                    </v-btn>
                  </div>
                  <div
                    :class="['response-text', pile.isResponseMonospace ? 'monospace' : '']"
                    v-html="pile.responseTextHTML"
                    @click="handleHTMLClick"
                  ></div>
                </div>

                <!-- RESPONSE STATS -->
                <div v-if="pile.responseStats !== null">
                  <div class="mt-2 mb-1 section-label">Statistics:</div>
                  <div class="d-flex flex-wrap align-center" style="gap: 6px 4px">
                    <div v-for="stat in pile.responseStats" class="stat-shield">
                      <div class="label">{{ stat.title }}</div>
                      <div :style="{ color: stat.color, backgroundColor: stat.background }" class="message">
                        {{ stat.value }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- RESPONSE OPTIONS -->
                <div>
                  <div class="mt-2 mb-1 section-label">Options:</div>
                  <div class="d-flex flex-wrap align-center" style="gap: 12px 8px">
                    <!-- STYLE -->
                    <v-switch
                      v-model="pile.isResponseMonospace"
                      :disabled="pile.queryRunning"
                      :ripple="false"
                      class="monospace-switch"
                      color="#EE8434"
                      label="Monospace"
                      hide-details
                    ></v-switch>

                    <!-- EXTRACT -->
                    <v-btn
                      :disabled="pile.queryRunning || extractButtonClicked"
                      :loading="extractButtonClicked"
                      :prepend-icon="mdiShape"
                      class="px-2"
                      density="comfortable"
                      title="Extract key phrases"
                      @click="onExtractButtonClick(pile.id)"
                    >
                      Extract
                    </v-btn>

                    <!-- LINK -->
                    <v-btn
                      :disabled="pile.queryRunning"
                      :loading="linkButtonClicked"
                      :prepend-icon="mdiVectorLine"
                      class="px-2"
                      density="comfortable"
                      title="Link response with documents"
                      @click="onLinkButtonClick(pile.id)"
                    >
                      Link
                    </v-btn>

                    <!-- SUGGEST -->
                    <v-btn
                      :disabled="pile.queryRunning"
                      :loading="suggestButtonClicked"
                      :prepend-icon="mdiBookshelf"
                      class="px-2"
                      density="comfortable"
                      title="Suggest related documents"
                      @click="onSuggestButtonClick(pile.id)"
                    >
                      Suggest
                    </v-btn>

                    <!-- BOOKMARK -->
                    <v-btn
                      :disabled="pile.queryRunning"
                      :prepend-icon="mdiBookmarkOutline"
                      class="px-2"
                      density="comfortable"
                      title="Bookmark response"
                      @click="bookmarkPile(pile.id)"
                    >
                      Bookmark
                    </v-btn>
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-expand-transition>
        </v-col>

        <!-- PILE KEYWORDS -->
        <v-col :class="pile.showResponse && pile.responseText !== null ? '' : 'pt-0'">
          <div class="pile-topics-wrapper">
            <span>Document topics:</span>
            <v-chip v-for="topic in getPileDocumentTopics(pile.id)" class="topic" density="compact" label>
              <span>{{ topic }}</span>
            </v-chip>
          </div>
        </v-col>
      </template>

      <!-- PILE NODES -->
      <v-col class="pt-0">
        <draggable
          v-model="pile.nodeList"
          :group="{ name: 'people', pull: 'clone' }"
          item-key="id"
          animation="150"
          class="dragArea list-group pile-drag-container"
          @change="(evt) => validateChangePileNode(evt, pile.id)"
        >
          <template #item="{ element, index }">
            <v-chip
              :color="getPileNodeColor(element)"
              closable
              label
              @click="setPileActiveNode(element, pile.id)"
              @click:close="removePileNode(element, index, pile.id)"
            >
              {{ element.name }}
            </v-chip>
          </template>
        </draggable>
      </v-col>

      <!-- PILE NODE TEXT -->
      <v-expand-transition>
        <div v-show="pile.activeNode !== null">
          <v-card-text v-html="pile.activeNodeHTML" class="pt-0 node-text" @click="handleHTMLClick"></v-card-text>
        </div>
      </v-expand-transition>
    </v-card>
  </v-col>
</template>

<script setup>
import { ref, inject, watch } from "vue";
import draggable from "vuedraggable";
import {
  mdiPencil,
  mdiPencilOutline,
  mdiBookmarkOutline,
  mdiContentCopy,
  mdiClose,
  mdiEraser,
  mdiShape,
  mdiVectorLine,
  mdiBookshelf,
} from "@mdi/js";

import PileQuery from "@/components/PileView/PileQuery.vue";

// get providers
const { entity } = inject("entity");

// get props
const props = defineProps([
  "pile",
  "enablePileEditName",
  "bookmarkPile",
  "clonePile",
  "removePile",
  "updatePileName",
  "togglePileResponseVisible",
  "runEntitySearch",
  "runPileTaskQuery",
  "runPileSearchDocumentsQuery",
  "getPileEntities",
  "clearPileEntities",
  "getPileLinks",
  "clearPileLinks",
  "selectLinkedSentences",
  "clearLinkedSentences",
  "getPileDocumentTopics",
  "validateChangePileNode",
  "setPileActiveNode",
  "removePileNode",
]);

// pile data (read-only!)
const pile = props.pile;

// pile update methods (to change pile data in parent PileView)
const enablePileEditName = props.enablePileEditName;
const bookmarkPile = props.bookmarkPile;
const clonePile = props.clonePile;
const removePile = props.removePile;
const updatePileName = props.updatePileName;
const togglePileResponseVisible = props.togglePileResponseVisible;
const runEntitySearch = props.runEntitySearch;
const runPileTaskQuery = props.runPileTaskQuery;
const runPileSearchDocumentsQuery = props.runPileSearchDocumentsQuery;
const getPileEntities = props.getPileEntities;
const clearPileEntities = props.clearPileEntities;
const getPileLinks = props.getPileLinks;
const clearPileLinks = props.clearPileLinks;
const selectLinkedSentences = props.selectLinkedSentences;
const clearLinkedSentences = props.clearLinkedSentences;
const getPileDocumentTopics = props.getPileDocumentTopics;
const validateChangePileNode = props.validateChangePileNode;
const setPileActiveNode = props.setPileActiveNode;
const removePileNode = props.removePileNode;

// set refs
const extractButtonClicked = ref(false);
const linkButtonClicked = ref(false);
const suggestButtonClicked = ref(false);

// set watchers
watch(
  () => pile.queryRunning,
  () => {
    if (pile.queryRunning == false) {
      linkButtonClicked.value = false;
      suggestButtonClicked.value = false;
    }
  }
);

/**
 * Number of cols to span in Vuetify grid scheme (i.e. bootstrap grid system)
 */
function getPileCols() {
  const hasActiveNode = pile.activeNode !== null;
  const hasResponseTextShowing = pile.responseText !== null && pile.showResponse;
  return hasActiveNode || hasResponseTextShowing ? 12 : 4;
}

/**
 * When done editing name, grab new name and update pile
 */
function savePileNameField(pileId) {
  const pileName = document.querySelector(`input[name="PileName${pileId}"]`).value;
  updatePileName(pileName, pileId);
}

/**
 * Calls extract entities function.
 */
function onExtractButtonClick(pileId) {
  extractButtonClicked.value = true;
  getPileEntities(pileId);
  extractButtonClicked.value = false;
}

/**
 * Calls link sentences function.
 */
function onLinkButtonClick(pileId) {
  linkButtonClicked.value = true;
  getPileLinks(pileId);
}

/**
 * Calls search query function.
 */
function onSuggestButtonClick(pileId) {
  suggestButtonClicked.value = true;
  runPileSearchDocumentsQuery(pileId);
}

function getPileNodeColor(node) {
  if (Object.hasOwn(node, "isNew") && node.isNew) {
    return "#EE8434";
  } else if (pile.activeNode !== null && pile.activeNode.id == node.id) {
    return "primary";
  } else {
    return "";
  }
}

/**
 * When clicking on response or node text, handle click event on target being clicked.
 *
 * See: <https://stackoverflow.com/a/53877473>
 */
function handleHTMLClick(evt) {
  const el = evt.target.closest(".search-term, .extracted-term, .entity-term, .linked-sentence"); // literal magic... how does it know...
  if (el) {
    if (
      el.classList.contains("search-term") ||
      el.classList.contains("extracted-term") ||
      el.classList.contains("entity-term")
    ) {
      // clicked on a boxed term, make it new entity to search
      const entityExists = entity.value.name !== null;
      const entityMatches = entityExists && el.innerText.toLowerCase() == entity.value.name.toLowerCase();
      if (!entityExists || !entityMatches) {
        runEntitySearch(el.innerText, true);
      }
    }
    if (el.classList.contains("linked-sentence")) {
      // clicked on a linked sentence
      if (el.classList.contains("selected")) {
        // sentence is already selected, deselect all selected sentences
        clearLinkedSentences(pile.id);
      } else {
        // select sentences based on linked sentence indices in data attribute
        const linkIndices = JSON.parse(el.dataset.linkIndices);
        selectLinkedSentences(linkIndices, pile.id);
      }
    }
  }
}
</script>

<style lang="scss">
.pile-controls-floating-wrapper {
  position: relative;
  width: 76px;
  top: 0px;
  left: calc(100% - 76px);
  margin-bottom: -24px;
  z-index: 1;

  > div {
    position: relative;
    top: -16px;
    left: 8px;
    padding: 2px;
  }
}

.pile-title-wrapper {
  font-family: "Teko", sans-serif;
  font-optical-sizing: auto;
  font-style: normal;
  font-weight: 700;
  font-size: 2rem;
  color: #86c232;

  span {
    max-width: 100%;
    white-space: pre-wrap;
    padding-top: 4px;
    line-height: 2rem;
  }
}

.pile-response-wrapper {
  background-color: rgb(238, 132, 52, 0.12);

  .section-label {
    font-family: "Teko", sans-serif;
    font-optical-sizing: auto;
    font-style: normal;
    font-weight: 700;
    font-size: 1.2rem;
    height: 24px;
    line-height: 24px;
    padding-top: 2px;
  }

  .stat-shield {
    display: flex;
    font-size: 0.8rem;

    .label {
      padding: 2px 4px 2px 6px;
      color: white;
      background-color: #555;
      border-top-left-radius: 4px;
      border-bottom-left-radius: 4px;
    }

    .message {
      padding: 2px 6px 2px 4px;
      color: #262626;
      background-color: #e0e0e0;
      border-top-right-radius: 4px;
      border-bottom-right-radius: 4px;
      text-shadow: 1px 1px 1px #262626;
    }
  }

  .response-text {
    padding-left: 8px;
    border-left: 4px solid #ccc;
    font-size: 0.8rem !important;
    white-space: pre-wrap;

    .search-term,
    .extracted-term,
    .entity-term {
      display: inline-block;
      border: 1px solid transparent;
      transition: 100ms;
      cursor: pointer;
    }

    .search-term.hovering,
    .extracted-term.hovering,
    .entity-term.hovering {
      border: 1px solid currentColor;
      transform: scale(1.1);
    }

    .linked-sentence {
      transition: 100ms;
      cursor: pointer;
    }

    .linked-sentence.hovering,
    .linked-sentence.selected {
      border-bottom-width: thick;
    }
  }

  .response-text.monospace {
    font-family: monospace;
  }

  .monospace-switch {
    .v-selection-control {
      height: 24px !important;
      min-height: 24px !important;
    }
  }
}

.pile-topics-wrapper {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;

  .topic span {
    font-size: 0.8rem;
    line-height: 1rem;
  }
}

.pile-drag-container {
  width: 100%;
  padding: 4px;
  display: flex;
  flex: 1 0 auto;
  flex-wrap: wrap;
  gap: 4px;
  border: 1px dashed #ccc;
}

.pile-drag-container:empty {
  font-family: monospace;
  text-align: center;
}

.pile-drag-container:empty:before {
  line-height: 1rem;
  font-size: 0.9rem;
  content: "Drag documents here to get started!";
}

.node-text {
  line-height: 1rem !important;
  font-size: 0.7rem !important;
  white-space: pre-wrap;

  .search-term,
  .extracted-term,
  .entity-term {
    display: inline-block;
    border: 1px solid transparent;
    transition: 100ms;
    cursor: pointer;
  }

  .search-term.hovering,
  .extracted-term.hovering,
  .entity-term.hovering {
    border: 1px solid currentColor;
    transform: scale(1.1);
  }

  .linked-sentence {
    transition: 100ms;
    cursor: pointer;
  }

  .linked-sentence.hovering,
  .linked-sentence.selected {
    border-bottom-width: thick;
  }
}
</style>
