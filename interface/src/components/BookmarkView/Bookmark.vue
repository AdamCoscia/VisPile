<template>
  <v-col>
    <!-- BOOKMARK CONTENTS -->
    <v-card>
      <!-- BOOKMARK TITLE -->
      <v-col :class="!bookmark.collapsed ? 'pb-1' : ''">
        <div class="d-flex align-center bookmark-title-wrapper">
          <template v-if="bookmark.editEnabled">
            <input
              :name="'BookmarkName' + bookmark.id"
              :placeholder="bookmark.name"
              :value="bookmark.name"
              type="text"
              class="bookmark-title-input"
              style="width: 100%"
            />
          </template>
          <template v-else>
            <div class="d-flex flex-1-1 align-center justify-space-between" style="gap: 4px">
              <div class="bookmark-title" @click="bookmark.collapsed = !bookmark.collapsed">
                {{ bookmark.name }}
              </div>
              <v-btn
                :icon="mdiClose"
                variant="text"
                size="20px"
                title="Remove bookmark"
                style="font-size: 0.8rem"
                @click="removeBookmark(bookmark.id)"
              ></v-btn>
            </div>
          </template>
        </div>
      </v-col>

      <!-- BOOKMARK BODY -->
      <v-expand-transition>
        <div v-show="!bookmark.collapsed">
          <!-- BOOKMARK SUBTITLE -->
          <v-col class="pt-0 pb-1">
            <div class="bookmark-subtitle">Last updated: {{ bookmark.updateHistory.at(-1).ts.toLocaleString() }}</div>
          </v-col>

          <!-- BOOKMARK ACTIONS -->
          <v-col class="pt-0 pb-2 d-flex flex-wrap" style="gap: 6px 4px">
            <!-- EDIT -->
            <v-btn
              :color="bookmark.editEnabled ? 'primary' : ''"
              :icon="bookmark.editEnabled ? mdiPencil : mdiPencilOutline"
              density="comfortable"
              size="small"
              title="Edit bookmark name"
              @click="bookmark.editEnabled ? saveBookmarkEditedFields(bookmark.id) : enableBookmarkEdit(bookmark.id)"
            >
            </v-btn>

            <!-- COPY -->
            <v-btn
              :disabled="bookmark.editEnabled || bookmarkEmpty"
              :icon="mdiContentCopy"
              density="comfortable"
              size="small"
              title="Copy bookmark"
              @click="cloneBookmark(bookmark.id)"
            >
            </v-btn>

            <!-- EXTRACT -->
            <!-- <v-btn
              :disabled="bookmark.editEnabled || bookmarkEmpty"
              :icon="mdiShape"
              density="comfortable"
              size="small"
              title="Extract key phrases"
            >
            </v-btn> -->

            <!-- LINK -->
            <!-- <v-btn
              :disabled="bookmark.editEnabled || bookmarkEmpty"
              :icon="mdiVectorLine"
              density="comfortable"
              size="small"
              title="Link text with documents"
            >
            </v-btn> -->

            <!-- SUGGEST -->
            <!-- <v-btn
              :disabled="bookmark.editEnabled || bookmarkEmpty"
              :icon="mdiBookshelf"
              density="comfortable"
              size="small"
              title="Suggest related documents"
            >
            </v-btn> -->
          </v-col>

          <!-- BOOKMARK BODY -->
          <v-col v-if="bookmarkContentShowing" class="py-0">
            <template v-if="bookmark.editEnabled">
              <!-- ENTITIES -->
              <v-combobox
                v-model="bookmark.entities"
                v-model:search="currentEntitySearch"
                :hide-no-data="false"
                class="mt-1 mb-2"
                density="comfortable"
                variant="underlined"
                label="Key words and phrases"
                clearable
                chips
                closable-chips
                hide-selected
                hide-details
                multiple
              >
                <template v-slot:no-data>
                  <v-list-item>
                    <v-list-item-title v-html="entitySearchHint"></v-list-item-title>
                  </v-list-item>
                </template>
              </v-combobox>

              <!-- TEXT -->
              <label class="bookmark-section-label">Text</label>
              <textarea
                :name="'BookmarkText' + bookmark.id"
                :placeholder="
                  bookmark.text ? bookmark.text : 'Click here and write a note to keep track of your findings'
                "
                :value="bookmark.text"
                class="bookmark-text-input"
                hide-details
                @input="
                  this.style.height = '';
                  this.style.height = `${this.scrollHeight + 2}px`;
                "
              />
            </template>
            <template v-else>
              <!-- ENTITIES -->
              <div v-if="bookmark.entities.length > 0" class="mb-2">
                <div class="d-flex justify-space-between">
                  <label class="bookmark-section-label">Key words and phrases</label>
                  <v-icon
                    :icon="mdiEraser"
                    size="14px"
                    title="Clear entities"
                    @click="clearBookmark(bookmark.id, 'entities')"
                  >
                  </v-icon>
                </div>
                <div class="bookmark-entities">
                  <v-chip v-for="entity in bookmark.entities" density="compact" color="#C95D63" label>
                    {{ entity }}
                  </v-chip>
                </div>
              </div>

              <!-- TEXT -->
              <div v-if="bookmark.text" class="mb-2">
                <div class="d-flex justify-space-between">
                  <label class="bookmark-section-label">Text</label>
                  <v-icon :icon="mdiEraser" size="14px" title="Clear text" @click="clearBookmark(bookmark.id, 'text')">
                  </v-icon>
                </div>
                <div class="bookmark-text">{{ bookmark.text }}</div>
              </div>
            </template>
          </v-col>

          <!-- DOCUMENTS -->
          <v-col class="pt-0">
            <div class="d-flex justify-space-between">
              <label class="bookmark-section-label">Documents</label>
              <v-icon
                v-if="bookmark.nodeList.length > 0"
                :icon="mdiEraser"
                size="14px"
                title="Clear documents"
                @click="clearBookmark(bookmark.id, 'nodeList')"
              >
              </v-icon>
            </div>
            <draggable
              v-model="bookmark.nodeList"
              :group="{ name: 'people', pull: 'clone' }"
              item-key="id"
              animation="150"
              class="dragArea list-group bookmark-drag-container"
              @change="(evt) => validateChangeBookmarkNode(evt, bookmark.id)"
            >
              <template #item="{ element, index }">
                <v-chip density="compact" closable label @click:close="removeBookmarkNode(index, bookmark.id)">
                  {{ element.name }}
                </v-chip>
              </template>
            </draggable>
          </v-col>
        </div>
      </v-expand-transition>
    </v-card>
  </v-col>
</template>

<script setup>
import { ref, computed } from "vue";
import draggable from "vuedraggable";
import {
  mdiPencil,
  mdiPencilOutline,
  mdiEraser,
  mdiContentCopy,
  mdiClose,
  mdiShape,
  mdiVectorLine,
  mdiBookshelf,
} from "@mdi/js";

// get props
const props = defineProps([
  "bookmark",
  "enableBookmarkEdit",
  "cloneBookmark",
  "removeBookmark",
  "saveBookmark",
  "clearBookmark",
  "validateChangeBookmarkNode",
  "removeBookmarkNode",
]);

// bookmark data (read-only!)
const bookmark = props.bookmark;

// bookmark update methods (to change bookmark data in parent BookmarkView)
const enableBookmarkEdit = props.enableBookmarkEdit;
const cloneBookmark = props.cloneBookmark;
const removeBookmark = props.removeBookmark;
const saveBookmark = props.saveBookmark;
const clearBookmark = props.clearBookmark;
const validateChangeBookmarkNode = props.validateChangeBookmarkNode;
const removeBookmarkNode = props.removeBookmarkNode;

// set refs
const currentEntitySearch = ref(""); // current key word or phrase being typed

// get computed
const entitySearchHint = computed(() => {
  if (currentEntitySearch.value === "") {
    return "Start typing a key word or phrase!";
  } else {
    return `Press <kbd>enter</kbd> to save "${currentEntitySearch.value}"`;
  }
});
const bookmarkEmpty = computed(() => {
  return !bookmark.text && bookmark.entities.length == 0 && bookmark.nodeList.length == 0;
});
const bookmarkContentShowing = computed(() => {
  return bookmark.editEnabled || bookmark.text || bookmark.entities.length > 0;
});

/**
 * When done editing, grab new name and text and update bookmark.
 */
function saveBookmarkEditedFields(bookmarkId) {
  const bookmarkName = document.querySelector(`input[name="BookmarkName${bookmarkId}"]`).value;
  const bookmarkText = document.querySelector(`textarea[name="BookmarkText${bookmarkId}"]`).value;
  saveBookmark(bookmarkName, bookmarkText, bookmarkId);
}
</script>

<style lang="scss">
.bookmark-title-wrapper {
  font-family: "Teko", sans-serif;
  font-optical-sizing: auto;
  font-style: normal;
  font-weight: 700;
  font-size: 1.3rem;

  .bookmark-title-input {
    caret-color: black;
  }

  .bookmark-title {
    padding-top: 4px;
    line-height: 1rem;
    word-break: break-word;
    user-select: none;
    cursor: pointer;
  }

  .bookmark-title:hover {
    text-decoration: underline;
  }
}

.bookmark-subtitle {
  font-size: 0.7rem;
  opacity: 0.6;
}

.bookmark-entities {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 4px;

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

.bookmark-text,
.bookmark-text-input {
  padding-left: 6px;
  border-left: 4px solid #ccc;
  line-height: 1rem;
  font-size: 0.7rem;
  white-space: pre-wrap;
}

.bookmark-section-label {
  font-size: 0.8rem;
  font-weight: 700;
  opacity: 0.6;
}

.bookmark-text-input {
  caret-color: black;
  width: 100%;
  border: 1px dashed #ccc;
}

.bookmark-drag-container {
  width: 100%;
  padding: 4px;
  display: flex;
  flex: 1 0 auto;
  flex-wrap: wrap;
  gap: 4px;
  border: 1px dashed #ccc;

  .v-chip__content {
    font-size: 0.75rem;
  }

  .v-chip__close {
    font-size: 0.8rem;
  }
}

.bookmark-drag-container:empty {
  font-family: monospace;
  text-align: center;
}

.bookmark-drag-container:empty:before {
  line-height: 0.9rem;
  font-size: 0.8rem;
  content: "Drag documents here to bookmark them!";
}
</style>
