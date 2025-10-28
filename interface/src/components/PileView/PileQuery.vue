<template>
  <v-col class="d-flex flex-wrap align-center" style="gap: 12px 8px">
    <!-- MODEL SELECT -->
    <v-select
      v-model="pile.model"
      :items="pile.models"
      :disabled="pile.queryRunning"
      label="Model"
      density="compact"
      variant="outlined"
      return-object
      hide-details
    ></v-select>

    <!-- TASK SELECT -->
    <v-select
      v-model="pile.model.task"
      :items="pile.model.tasks"
      :disabled="pile.queryRunning"
      label="Task"
      density="compact"
      variant="outlined"
      return-object
      hide-details
    ></v-select>

    <!-- QUERY BUTTON -->
    <v-btn
      :disabled="pile.nodeList.length == 0 || pile.queryRunning"
      :loading="queryButtonClicked"
      @click="onQueryButtonClick(pile.id)"
    >
      Query
    </v-btn>

    <!-- SETTINGS -->
    <template v-if="pile.model.settings !== null || pile.model.task.settings !== null">
      <v-menu :close-on-content-click="false" :disabled="pile.queryRunning" location="bottom center" offset="16">
        <template v-slot:activator="{ props: menu }">
          <v-tooltip location="top center">
            <template v-slot:activator="{ props: tooltip }">
              <v-btn
                v-bind="mergeProps(menu, tooltip)"
                :disabled="pile.queryRunning"
                :icon="mdiCog"
                density="comfortable"
                variant="flat"
              ></v-btn>
            </template>
            <span>Query settings</span>
          </v-tooltip>
        </template>
        <v-card title="Query settings" subtitle="Customize your query!" width="600" class="query-settings">
          <v-card-text>
            <!-- MODEL SETTINGS -->
            <v-row class="model-settings" v-if="pile.model.settings !== null">
              <v-col class="d-flex flex-column">
                <div class="mb-1 section-label">Model: {{ pile.model.title }}</div>

                <!-- TEMPERATURE -->
                <div class="section-wrapper" v-if="Object.hasOwn(pile.model.settings, 'temperature')">
                  <div class="mb-1"><span class="setting-label">Temperature</span>🔥</div>
                  <v-slider
                    v-model="pile.model.settings.temperature"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    :ticks="d3.range(0, 1.1, 0.1).map((x) => Number(x).toFixed(1))"
                    class="temperature-slider"
                    color="#EE8434"
                    show-ticks="always"
                    hide-details
                  ></v-slider>
                </div>
              </v-col>
            </v-row>

            <!-- TASK SETTINGS -->
            <v-row class="task-settings" v-if="pile.model.task.settings !== null">
              <v-col class="d-flex flex-column">
                <div class="mb-1 section-label">Task: {{ pile.model.task.title }}</div>

                <!-- PROMPT -->
                <div class="section-wrapper" v-if="pile.model.task.value !== 'custom'">
                  <div class="mb-1"><span class="setting-label">Prompt</span></div>
                  <div class="prompt-text">
                    <!-- SUMMARIZE PROMPT -->
                    <span
                      v-if="pile.model.task.value == 'summarize'"
                      class="prompt"
                      v-html="getSummarizePrompt(pile)"
                    ></span>
                    <!-- EXTRACT PROMPT -->
                    <span
                      v-else-if="pile.model.task.value == 'extract_entities'"
                      class="prompt"
                      v-html="getExtractPrompt(pile)"
                    ></span>
                    <!-- EXPLAIN PROMPT -->
                    <span
                      v-else-if="pile.model.task.value == 'explain_concepts'"
                      class="prompt"
                      v-html="getExplainPrompt(pile)"
                    ></span>
                    <!-- ANSWER PROMPT -->
                    <span
                      v-else-if="pile.model.task.value == 'answer_questions'"
                      class="prompt"
                      v-html="getAnswerPrompt(pile)"
                    ></span>
                    <!-- ALL OTHER PROMPTS -->
                    <span
                      v-else
                      class="prompt"
                      v-html="pile.model.task.prompt[pile.nodeList.length == 1 ? 'single' : 'multiple']"
                    ></span>
                    <span>&nbsp;</span>
                    <span class="instructions" v-html="pile.model.task.settings.instructions"></span>
                  </div>
                </div>

                <!-- SUMMARY LENGTH -->
                <div class="section-wrapper" v-if="Object.hasOwn(pile.model.task.settings, 'summary_length')">
                  <div class="mb-1"><span class="setting-label">Summary Length</span></div>
                  <v-btn-toggle
                    v-model="pile.model.task.settings.summary_length"
                    variant="outlined"
                    density="compact"
                    mandatory
                  >
                    <v-btn value="concise">
                      <span class="pr-1">Concise</span>
                      <v-icon v-if="pile.model.task.settings.summary_length == 'concise'" :icon="mdiCheckBold"></v-icon>
                    </v-btn>
                    <v-btn value="verbose">
                      <span class="pr-1">Verbose</span>
                      <v-icon v-if="pile.model.task.settings.summary_length == 'verbose'" :icon="mdiCheckBold"></v-icon>
                    </v-btn>
                  </v-btn-toggle>
                </div>

                <!-- ENTITY -->
                <div class="section-wrapper" v-if="Object.hasOwn(pile.model.task.settings, 'entity')">
                  <div class="mb-1"><span class="setting-label">Entity Type</span></div>
                  <v-select
                    v-model="pile.model.task.settings.entity"
                    :items="['person', 'location', 'organization', 'datetime']"
                    density="compact"
                    variant="outlined"
                    hide-details
                  >
                  </v-select>
                </div>

                <!-- CONCEPTS -->
                <div class="section-wrapper" v-if="Object.hasOwn(pile.model.task.settings, 'concepts')">
                  <div class="mb-1"><span class="setting-label">Concepts</span></div>
                  <v-combobox
                    v-model="pile.model.task.settings.concepts"
                    v-model:search="currentConceptsSearch"
                    :hide-no-data="false"
                    density="comfortable"
                    variant="outlined"
                    multiple
                    clearable
                    chips
                    closable-chips
                    hide-selected
                    hide-details
                  >
                    <template v-slot:no-data>
                      <v-list-item>
                        <v-list-item-title v-html="conceptsSearchHint"></v-list-item-title>
                      </v-list-item>
                    </template>
                  </v-combobox>
                </div>

                <!-- QUESTIONS -->
                <div class="section-wrapper" v-if="Object.hasOwn(pile.model.task.settings, 'questions')">
                  <div class="mb-1"><span class="setting-label">Questions</span></div>
                  <v-list max-height="100px" variant="outlined" density="compact">
                    <v-list-item
                      v-for="(question, index) in pile.model.task.settings.questions"
                      :key="index"
                      class="mb-2 mx-1"
                      rounded
                    >
                      <template v-slot:prepend>
                        <span class="mr-2">{{ index + 1 }}.</span>
                      </template>
                      <v-text-field
                        v-model="pile.model.task.settings.questions[index]"
                        class="questions-textfield"
                        placeholder="Click here to type a question"
                        variant="plain"
                        hide-details
                      ></v-text-field>
                      <template v-slot:append>
                        <v-icon :icon="mdiClose" @click="pile.model.task.settings.questions.splice(index, 1)"></v-icon>
                      </template>
                    </v-list-item>
                    <div class="px-1">
                      <v-btn block @click="pile.model.task.settings.questions.push('')">Add question</v-btn>
                    </div>
                  </v-list>
                </div>

                <!-- ADDITIONAL INSTRUCTIONS -->
                <div class="section-wrapper" v-if="Object.hasOwn(pile.model.task.settings, 'instructions')">
                  <div class="mb-1"><span class="setting-label">Additional Instructions</span></div>
                  <v-textarea
                    v-model:model-value="pile.model.task.settings.instructions"
                    class="instructions-textarea"
                    placeholder='e.g., "Return your response as a bulleted list."'
                    variant="outlined"
                    rows="1"
                    hide-details
                    auto-grow
                  ></v-textarea>
                </div>

                <!-- CUSTOM PROMPT -->
                <div class="section-wrapper" v-if="Object.hasOwn(pile.model.task.settings, 'prompt')">
                  <v-select
                    :items="customPromptExamples"
                    class="mt-2 pb-2"
                    label="Example prompts"
                    density="compact"
                    variant="outlined"
                    clearable
                    hide-details
                    v-on:update:model-value="(val) => (pile.model.task.settings.prompt = val)"
                  ></v-select>
                  <v-textarea
                    v-model="pile.model.task.settings.prompt"
                    class="instructions-textarea"
                    placeholder="Type or copy/paste any prompt you like!"
                    variant="outlined"
                    hide-details
                    auto-grow
                  ></v-textarea>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-menu>
    </template>

    <!-- SHOW/HIDE -->
    <v-tooltip
      v-if="pile.responseText !== null"
      :text="pile.showResponse ? 'Hide response' : 'Show response'"
      location="top center"
    >
      <template v-slot:activator="{ props }">
        <v-btn
          v-bind="props"
          :disabled="pile.responseText == null"
          :color="pile.showResponse ? '#EE8434' : ''"
          :icon="pile.showResponse ? mdiEye : mdiEyeClosed"
          density="comfortable"
          variant="flat"
          @click="togglePileResponseVisible(pile.id)"
        ></v-btn>
      </template>
    </v-tooltip>
  </v-col>
</template>

<script setup>
import { ref, computed, watch, mergeProps } from "vue";
import * as d3 from "d3";
import { mdiEye, mdiEyeClosed, mdiCog, mdiClose, mdiCheckBold } from "@mdi/js";

// get props
const props = defineProps(["pile", "runPileQuery", "togglePileResponseVisible"]);

// pile data (read-only!)
const pile = props.pile;

// pile update methods (to change pile data in parent PileView)
const runPileQuery = props.runPileQuery;
const togglePileResponseVisible = props.togglePileResponseVisible;

// set refs
const queryButtonClicked = ref(false);
const currentConceptsSearch = ref(""); // current key word or phrase being typed

// get computed
const conceptsSearchHint = computed(() => {
  if (currentConceptsSearch.value === "") {
    return "Start typing a concept!";
  } else {
    return `Press <kbd>enter</kbd> to save "${currentConceptsSearch.value}"`;
  }
});

// get data
const customPromptExamples = [
  { title: "Counting words", value: "Please find all of the most common words and count them" },
  { title: "Finding relationships", value: "Create a table of the people and relationships in the documents" },
];

// set watchers
watch(
  () => pile.queryRunning,
  () => {
    if (pile.queryRunning == false) {
      queryButtonClicked.value = false;
    }
  }
);

/**
 * Calls task query function.
 */
function onQueryButtonClick(pileId) {
  queryButtonClicked.value = true;
  runPileQuery(pileId);
}

/**
 * Get summarize prompt based on user settings.
 */
function getSummarizePrompt(pile) {
  const promptType = pile.nodeList.length == 1 ? "single" : "multiple";
  const summaryType = pile.model.task.settings.summary_length;
  return pile.model.task.prompt[promptType][summaryType];
}

/**
 * Get extract prompt based on user settings.
 */
function getExtractPrompt(pile) {
  const promptType = pile.nodeList.length == 1 ? "single" : "multiple";
  const entityType = pile.model.task.settings.entity;
  return pile.model.task.prompt[promptType][entityType];
}

/**
 * Get explain prompt based on user settings.
 */
function getExplainPrompt(pile) {
  const promptType = pile.nodeList.length == 1 ? "single" : "multiple";
  const concepts = pile.model.task.settings.concepts.map((x) => `"${x}"`).join(", ");
  return pile.model.task.prompt[promptType].replace("{concepts}", concepts);
}

/**
 * Get answer prompt based on user settings.
 */
function getAnswerPrompt(pile) {
  const promptType = pile.nodeList.length == 1 ? "single" : "multiple";
  const questions = pile.model.task.settings.questions.map((x) => `"${x}"`).join(", ");
  return pile.model.task.prompt[promptType].replace("{questions}", questions);
}
</script>

<style lang="scss">
.query-settings {
  .section-label {
    font-family: "Teko", sans-serif;
    font-optical-sizing: auto;
    font-style: normal;
    font-weight: 700;
    font-size: 1.5rem;
  }

  .setting-label {
    font-size: 1rem;
    opacity: 0.5;
    padding-bottom: 4px;

    span {
      opacity: 1;
    }
  }

  .section-wrapper {
    &:not(:last-child) {
      margin-bottom: 8px;
    }
  }

  .prompt-text {
    font-family: monospace;
    font-size: 0.8rem;
    padding-left: 8px;
    border-left: 4px solid #ccc;
    white-space: pre-line;

    .instructions {
      font-weight: 700;
      color: #4448ac;
    }
  }

  .temperature-slider {
    padding-bottom: 4px;

    .v-slider-track__tick-label {
      font-size: 0.8rem;
    }
  }

  .questions-textfield {
    .v-field__input {
      padding: 0 !important;
      min-height: 0 !important;
      height: 24px !important;
    }
  }
}
</style>
