<template>
  <v-col class="d-flex flex-column overflow-hidden" style="max-height: 100%">
    <!-- HEADER -->
    <div class="d-flex flex-wrap justify-space-between">
      <!-- TITLE -->
      <header class="ml-3 bookmarks-title">Notes</header>

      <!-- ACTIONS -->
      <div style="padding-top: 2px">
        <v-menu :close-on-content-click="false" location="left bottom" offset="10">
          <template v-slot:activator="{ props: menu }">
            <v-tooltip location="top center">
              <template v-slot:activator="{ props: tooltip }">
                <v-icon v-bind="mergeProps(menu, tooltip)" :icon="mdiCog"></v-icon>
              </template>
              <span>Bookmark settings</span>
            </v-tooltip>
          </template>
          <v-card title="Bookmark settings" subtitle="Filter bookmarks" min-width="300">
            <v-card-text>
              <v-select
                v-model="selectedBookmarks"
                :disabled="bookmarks.length == 0"
                :items="bookmarks"
                item-title="name"
                label="Filter bookmarks"
                density="compact"
                variant="outlined"
                multiple
                return-object
                hide-details
              >
                <template v-slot:prepend-item>
                  <v-list-item title="Select All" @click="toggleBookmarkSelectAll">
                    <template v-slot:prepend>
                      <v-checkbox-btn
                        :color="someBookmarksSelected ? '#4448ac' : undefined"
                        :indeterminate="someBookmarksSelected && !allBookmarksSelected"
                        :model-value="allBookmarksSelected"
                      ></v-checkbox-btn>
                    </template>
                  </v-list-item>
                  <v-divider class="mt-2"></v-divider>
                </template>
                <template v-slot:selection="{ item, index }">
                  <span v-if="index < 1">
                    {{ item.title }}
                  </span>
                  <span v-if="index === 1" class="text-caption align-self-center"
                    >(+{{ selectedBookmarks.length - 1 }})</span
                  >
                </template>
              </v-select>
            </v-card-text>
          </v-card>
        </v-menu>
      </div>
    </div>

    <div class="mt-2">
      <v-btn :prepend-icon="mdiBookmarkOutline" block @click="() => createBookmark()">New bookmark</v-btn>
    </div>

    <v-divider class="my-4"></v-divider>

    <!-- RESULTS -->
    <div class="overflow-auto pa-3" style="margin: -12px">
      <template v-if="bookmarks.length == 0">
        <div>
          No bookmarks yet. Click the button above or click a <v-icon :icon="mdiBookmarkOutline"></v-icon>bookmark icon
          to get started!
        </div>
      </template>
      <template v-else>
        <Bookmark
          v-for="bookmark in selectedBookmarks"
          class="pa-0 mb-2"
          :key="bookmark.id"
          :bookmark="bookmark"
          :enable-bookmark-edit="enableBookmarkEdit"
          :clone-bookmark="cloneBookmark"
          :remove-bookmark="removeBookmark"
          :save-bookmark="saveBookmark"
          :clear-bookmark="clearBookmark"
          :validate-change-bookmark-node="validateChangeBookmarkNode"
          :remove-bookmark-node="removeBookmarkNode"
        ></Bookmark>
      </template>
    </div>
  </v-col>
</template>

<script setup>
import { ref, inject, computed, nextTick, toRaw, mergeProps } from "vue";
import { getCopyName } from "@/utils";
import { mdiCog, mdiBookmarkOutline } from "@mdi/js";

import Bookmark from "@/components/BookmarkView/Bookmark.vue";

// define expose
defineExpose({ createBookmarkFromPile }); // these are available in parent Page.vue

// get providers
const { documents } = inject("documents");
const { bookmarks, updateBookmarks } = inject("bookmarks");

// set refs
const bookmarkId = ref(0); // continously incrementing unique piling id
const nodeData = ref({}); // node data look up
const selectedBookmarks = ref([]); // only selected bookmarks

const toggleBookmarkSelectAll = () => {
  selectedBookmarks.value = allBookmarksSelected.value ? [] : bookmarks.value.slice();
};

// get node data
nodeData.value = Object.fromEntries(
  documents.value.map((d) => {
    return [d.id, d];
  })
);

// when keywords change, update all active node's HTML
// watch(keywords, () => {
//   updateAllActiveNodeHTML();
// });

// get computed
const allBookmarksSelected = computed(() => {
  return bookmarks.value.length == selectedBookmarks.value.length;
});
const someBookmarksSelected = computed(() => {
  return selectedBookmarks.value.length > 0;
});

/**
 * Add new bookmark, adding/overwriting any properties from `bookmarkOpts`.
 */
function createBookmark(bookmarkOpts = {}) {
  const ts = new Date(Date.now());
  const defaultBookmark = {
    id: bookmarkId.value,
    name: `Bookmark ${bookmarkId.value + 1}`,
    createdAt: ts,
    updateHistory: [],
    collapsed: true,
    editEnabled: false,
    entities: [],
    text: "",
    nodeList: [],
  };
  const newBookmark = {
    ...defaultBookmark,
    ...bookmarkOpts, // overwrites properties with the same key
  };
  newBookmark.updateHistory.push({ event: "createBookmark", ts: ts });
  updateBookmarks((bookmarks) => bookmarks.value.push(newBookmark));
  selectedBookmarks.value.push(newBookmark);
  bookmarkId.value++;
}

/**
 * Create a bookfrom from a pile; called in PileView.vue
 */
function createBookmarkFromPile(pileProps) {
  createBookmark({ name: pileProps.name, text: pileProps.responseText, nodeList: pileProps.nodeList });
}

/**
 * Clone bookmark at `bookmarkIndex`.
 */
function cloneBookmark(bookmarkId) {
  const bookmarkIndex = bookmarks.value.findIndex((bookmark) => bookmark.id == bookmarkId);
  const copyName = bookmarks.value[bookmarkIndex].name.slice() + " - Copy";
  const newName = getCopyName(
    bookmarks.value.map((x) => x.name),
    copyName
  );
  createBookmark({
    name: newName,
    entities: structuredClone(bookmarks.value[bookmarkIndex].entities.map((entity) => toRaw(entity))), // create deep copy
    text: bookmarks.value[bookmarkIndex].text.slice(),
    nodeList: structuredClone(bookmarks.value[bookmarkIndex].nodeList.map((node) => toRaw(node))), // create deep copy
  });
}

/**
 * Remove bookmark at `bookmarkIndex`.
 */
function removeBookmark(bookmarkId) {
  const bookmarkIndex = bookmarks.value.findIndex((bookmark) => bookmark.id == bookmarkId);
  updateBookmarks((bookmarks) => bookmarks.value.splice(bookmarkIndex, 1));
  const selectedBookmarkIndex = selectedBookmarks.value.findIndex((bookmark) => bookmark.id == bookmarkId);
  selectedBookmarks.value.splice(selectedBookmarkIndex, 1);
}

/**
 * Set bookmark into edit name mode and focus input element automatically.
 */
function enableBookmarkEdit(bookmarkId) {
  const bookmarkIndex = bookmarks.value.findIndex((bookmark) => bookmark.id == bookmarkId);
  updateBookmarks((bookmarks) => (bookmarks.value[bookmarkIndex].editEnabled = true));
  nextTick(() => {
    document.querySelector(`input[name="BookmarkName${bookmarkId}"]`).focus();
    const bookmarkTextArea = document.querySelector(`textarea[name="BookmarkText${bookmarkId}"]`);
    bookmarkTextArea.style.height = "";
    bookmarkTextArea.style.height = `${bookmarkTextArea.scrollHeight + 2}px`;
  });
}

/**
 * Save bookmark name and text when user un-clicks edit button.
 */
function saveBookmark(newBookmarkName, newBookmarkText, bookmarkId) {
  const bookmarkIndex = bookmarks.value.findIndex((bookmark) => bookmark.id == bookmarkId);
  if (newBookmarkName !== "") updateBookmarks((bookmarks) => (bookmarks.value[bookmarkIndex].name = newBookmarkName));
  if (newBookmarkText !== "") updateBookmarks((bookmarks) => (bookmarks.value[bookmarkIndex].text = newBookmarkText));
  updateBookmarks((bookmarks) => (bookmarks.value[bookmarkIndex].editEnabled = false));
  updateBookmarks((bookmarks) => {
    bookmarks.value[bookmarkIndex].updateHistory.push({
      event: "saveBookmark",
      ts: new Date(Date.now()),
    });
  });
}

/**
 * Clear bookmark `section` when user clicks erase button.
 */
function clearBookmark(bookmarkId, bookmarkSection) {
  const bookmarkIndex = bookmarks.value.findIndex((bookmark) => bookmark.id == bookmarkId);
  if (bookmarkSection == "text") updateBookmarks((bookmarks) => (bookmarks.value[bookmarkIndex].text = ""));
  if (bookmarkSection == "entities") updateBookmarks((bookmarks) => (bookmarks.value[bookmarkIndex].entities = []));
  if (bookmarkSection == "nodeList") updateBookmarks((bookmarks) => (bookmarks.value[bookmarkIndex].nodeList = []));
  updateBookmarks((bookmarks) => {
    bookmarks.value[bookmarkIndex].updateHistory.push({
      event: "clearBookmark",
      ts: new Date(Date.now()),
    });
  });
}

/**
 * Perform actions when draggable bookmark changes:
 * 1. prevent duplicates when adding to a bookmark.
 */
function validateChangeBookmarkNode(evt, bookmarkId) {
  const bookmarkIndex = bookmarks.value.findIndex((bookmark) => bookmark.id == bookmarkId);
  const bookmarkNodeList = bookmarks.value[bookmarkIndex].nodeList;
  if (Object.hasOwn(evt, "added")) {
    if (bookmarkNodeList.filter((d) => d.id == evt.added.element.id).length > 1) {
      // remove element added if duplicates exist in the bookmark
      updateBookmarks((bookmarks) => bookmarks.value[bookmarkIndex].nodeList.splice(evt.added.newIndex, 1));
    } else {
      // new node added
      updateBookmarks((bookmarks) => {
        bookmarks.value[bookmarkIndex].updateHistory.push({
          event: "addBookmarkNode",
          ts: new Date(Date.now()),
        });
      });
    }
  }
}

/**
 * Remove node from bookmark.
 */
function removeBookmarkNode(bookmarkNodeIndex, bookmarkId) {
  const bookmarkIndex = bookmarks.value.findIndex((bookmark) => bookmark.id == bookmarkId);
  updateBookmarks((bookmarks) => bookmarks.value[bookmarkIndex].nodeList.splice(bookmarkNodeIndex, 1));
  updateBookmarks((bookmarks) => {
    bookmarks.value[bookmarkIndex].updateHistory.push({
      event: "removeBookmarkNode",
      ts: new Date(Date.now()),
    });
  });
}
</script>

<style lang="scss">
.bookmarks-title {
  font-family: "Teko", sans-serif;
  font-optical-sizing: auto;
  font-style: normal;
  font-weight: 700;
  font-size: 1.5rem;
  text-shadow: 1px 2px 2px black;
  color: white;
  text-align: right;
  height: 32px;
}

.bookmarks-section-title {
  font-family: "Teko", sans-serif;
  font-optical-sizing: auto;
  font-style: normal;
  font-weight: 100;
  font-size: 1.5rem;
  line-height: 1.5rem;
  color: white;
}
</style>
