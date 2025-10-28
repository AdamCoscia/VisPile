<template>
  <v-app class="overflow-hidden">
    <!-- APP BAR -->
    <v-app-bar class="app-bar" color="#262626" elevation="1">
      <div class="decoration">
        <img :src="decorationSVG" />
      </div>
      <div class="header" style="gap: 12px">
        <div class="title">VisPile</div>
        <div class="subtitle">Interactive Multi-Document 🗺️ Exploration and 📚 Synthesis</div>
      </div>
    </v-app-bar>

    <!-- SOURCE VIEW -->
    <v-navigation-drawer v-model="sourceViewDrawerShown" location="left" width="300" color="#515151" permanent>
      <div :style="sourceViewDrawerStyle" class="expand-toggle">
        <v-tooltip
          :text="sourceViewDrawerShown ? 'Close panel' : 'Open panel'"
          :location="sourceViewDrawerShown ? 'top center' : 'right center'"
        >
          <template v-slot:activator="{ props }">
            <v-btn
              v-bind="props"
              :icon="sourceViewDrawerShown ? mdiChevronDoubleLeft : mdiChevronDoubleRight"
              fab
              size="x-small"
              @click="sourceViewDrawerShown = !sourceViewDrawerShown"
            >
            </v-btn>
          </template>
        </v-tooltip>
      </div>
      <SourceView
        v-if="documents !== null"
        ref="sourceView"
        @request-create-pile-from-selected="completeRequestCreatePileFromSelected"
      />
      <div v-else>Error loading documents, cannot render application</div>
    </v-navigation-drawer>

    <!-- MAIN VIEW -->
    <v-main style="max-height: 100vh">
      <PileView
        v-if="documents !== null"
        ref="pileView"
        @request-create-bookmark-from-pile="completeRequestCreateBookmarkFromPile"
      />
    </v-main>

    <!-- BOOKMARK  VIEW -->
    <v-navigation-drawer v-model="bookmarkViewDrawerShown" location="right" width="250" color="#048A81" permanent>
      <div :style="bookmarkViewDrawerStyle" class="expand-toggle">
        <v-tooltip
          :text="bookmarkViewDrawerShown ? 'Close panel' : 'Open panel'"
          :location="bookmarkViewDrawerShown ? 'top center' : 'left center'"
        >
          <template v-slot:activator="{ props }">
            <v-btn
              v-bind="props"
              :icon="bookmarkViewDrawerShown ? mdiChevronDoubleRight : mdiChevronDoubleLeft"
              fab
              size="x-small"
              @click="bookmarkViewDrawerShown = !bookmarkViewDrawerShown"
            >
            </v-btn>
          </template>
        </v-tooltip>
      </div>
      <BookmarkView v-if="documents !== null" ref="bookmarkView" />
    </v-navigation-drawer>

    <!-- TOOLTIP -->
    <div class="tooltip"></div>
  </v-app>
</template>

<script setup>
import { ref, provide, computed } from "vue";
import { mdiChevronDoubleRight, mdiChevronDoubleLeft } from "@mdi/js";

import SourceView from "@/components/SourceView.vue";
import PileView from "@/components/PileView.vue";
import BookmarkView from "@/components/BookmarkView.vue";

import defaultModels from "@/assets/data/models.json";
import decorationSVG from "@/assets/icons/decoration.svg";

import vastDocs from "@/assets/data/vast/documents.json";
import vastKGNodes from "@/assets/data/vast/nodes.json";
import vastKGLinks from "@/assets/data/vast/links.json";

// set refs
const sourceView = ref(null);
const pileView = ref(null);
const bookmarkView = ref(null);
const sourceViewDrawerShown = ref(true); // whether the source view drawer is open
const bookmarkViewDrawerShown = ref(true); // whether the bookmark view drawer is open

const documents = ref([]); // list of text documents
const searchTerms = ref([]); // list of search terms to filter documents
const searchTermSettings = ref({ patternMatch: "whole-word", documentContains: "every" }); // search settings
const entity = ref({ name: null, facts: [], related: [], similar: [] }); // entity of interest to look up in the knowledge graph
const piles = ref([]); // list of piles
const bookmarks = ref([]); // list of artifacts (documents, summaries, etc.) bookmarked by user
const models = ref([]); // LLM models and their tasks available in backend server
const knowledgeGraph = ref({ nodes: vastKGNodes, links: vastKGLinks }); // knowledge graph nodes and links

models.value = defaultModels.filter((model) => model.allowed); // filter default models
models.value.forEach((model) => (model.task = model.tasks[0])); // set default tasks for each model

const updateDocuments = (update) => update(documents);
const updateSearchTerms = (update) => update(searchTerms);
const updateSearchTermSettings = (update) => update(searchTermSettings);
const updateEntity = (update) => update(entity);
const updatePiles = (update) => update(piles);
const updateBookmarks = (update) => update(bookmarks);

documents.value = vastDocs;
documents.value.forEach((document) => {
  if (document.date !== null) {
    document.date = new Date(document.date).toLocaleDateString("en-ZA");
    // .toLocaleDateString('en-US', {year: 'numeric', month: '2-digit', day: '2-digit'}); // 08/19/2020 (month and day with two digits)
    // .toLocaleDateString('en-ZA'); // 2020/08/19 (year/month/day) notice the different locale
    // .toLocaleDateString('en-CA'); // 2020-08-19 (year-month-day) notice the different locale
  } else {
    document.date = "undefined";
  }
});

// set providers
provide("documents", { documents, updateDocuments });
provide("searchTerms", { searchTerms, updateSearchTerms, searchTermSettings, updateSearchTermSettings });
provide("entity", { entity, updateEntity });
provide("piles", { piles, updatePiles });
provide("bookmarks", { bookmarks, updateBookmarks });
provide("models", { models });
provide("knowledgeGraph", { knowledgeGraph });

// set computed
const sourceViewDrawerStyle = computed(() => {
  return { right: sourceViewDrawerShown.value ? `${-32 + 16}px` : `${-32 - 16}px` };
});
const bookmarkViewDrawerStyle = computed(() => {
  return { right: bookmarkViewDrawerShown.value ? `${250 - 16}px` : `${250 + 16}px` };
});

/**
 * Call function in PileView to create pile with `pileProps`
 */
function completeRequestCreatePileFromSelected(pileProps) {
  pileView.value.createPile(pileProps);
}

/**
 * Call function in BookmarkView to create bookmark from pile
 */
function completeRequestCreateBookmarkFromPile(pileProps) {
  bookmarkView.value.createBookmarkFromPile(pileProps);
  bookmarkViewDrawerShown.value = true; // open bookmark drawer
}
</script>

<style lang="scss">
.app-bar {
  white-space: nowrap;

  .decoration {
    position: absolute;
    bottom: 0;
    z-index: -1;
    height: 64px;
    width: 64px;
  }

  .header {
    display: flex;
    align-items: center;
    flex: 1 0 auto;
    margin-left: 24px;
    margin-top: 8px;

    .title {
      font-family: "Teko", sans-serif;
      font-optical-sizing: auto;
      font-style: normal;
      font-weight: 700;
      font-size: 3rem;
      color: #86c232;
    }

    .subtitle {
      font-family: "Teko", sans-serif;
      font-optical-sizing: auto;
      font-style: normal;
      font-weight: 700;
      font-size: 2rem;
      color: white;
      text-shadow: 1px 2px 2px black;
    }
  }
}

.expand-toggle {
  position: absolute;
  z-index: 1;
  top: 6px;

  .v-btn {
    border: 1px solid grey;
  }

  .v-btn__content {
    font-size: 1rem;
  }
}

.tooltip {
  position: absolute;
  z-index: 1087;
  display: none; /* hide by default */
  opacity: 0; /* hide by default */
  max-width: 500px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 4px;
  background-color: white;
  box-sizing: border-box;
  box-shadow: rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px;
  white-space: pre-wrap;
  font-size: 0.6rem;
}

.search-term {
  padding: 0 4px;
  font-weight: 700;
  background-color: rgba(255, 234, 0);
  opacity: 0.75;
  border-radius: 4px;
}

.entity-term {
  padding: 0 4px;
  font-weight: 700;
  background-color: rgba(68, 72, 172, 0.12);
  color: rgb(68, 72, 172);
  border-radius: 4px;
}

.extracted-term {
  padding: 0 4px;
  font-weight: 700;
  background-color: rgba(201, 93, 99, 0.12);
  color: rgb(201, 93, 99);
  border-radius: 4px;
}

.linked-sentence {
  border-bottom-left-radius: 5px;
  border-bottom-right-radius: 5px;
  border-bottom-width: medium;
  border-bottom-style: solid;
}
</style>
