<template>
  <v-list class="pa-0 file-list-container" density="compact">
    <template v-for="(node, i) in nodesList">
      <v-list-group v-if="node.children && node.children.length">
        <template v-slot:activator="groupActivator">
          <v-tooltip text="Right-click to select all documents!" open-delay="750">
            <template v-slot:activator="tooltipActivator">
              <v-list-item
                v-bind="{ ...groupActivator.props, ...tooltipActivator.props }"
                :class="['parent-node', someNodesSelected(node.children) ? 'selected' : '']"
                :style="{ paddingInline: '0px !important', borderLeft: getDirectoryBorder(node) }"
                base-color="#515151"
                variant="flat"
                @contextmenu.prevent="selectAllNodes(node.children)"
              >
                <template v-slot:prepend>
                  <v-icon
                    :icon="groupActivator.isOpen ? mdiChevronDown : mdiChevronRight"
                    size="small"
                    density="compact"
                  ></v-icon>
                </template>
                <div class="d-flex align-center">
                  <v-icon
                    :icon="mdiFolder"
                    :style="{ color: getNodeColor(node) }"
                    size="small"
                    density="compact"
                  ></v-icon>
                  <span class="pl-1 title">
                    {{ getNodeName(node) }}
                  </span>
                </div>
                <template v-slot:append>
                  <span class="px-1 directory-numfiles-message">{{ getDirectoryNumFilesMessage(node) }}</span>
                </template>
              </v-list-item>
            </template>
          </v-tooltip>
        </template>
        <node-list
          :nodes="d3.sort(node.children, (d) => -d.height)"
          :color="color"
          :nodes-sort-by="nodesSortBy"
          :search-terms="searchTerms"
          :search-term-pattern-match="searchTermPatternMatch"
          :entity="entity"
          :update-node-selections="updateNodeSelections"
          class="py-0"
          style="margin-left: 6px"
        />
      </v-list-group>
      <draggable
        v-else
        :list="[{ name: node.data.name, id: node.data.id }]"
        :group="{ name: 'people', pull: 'clone', put: false }"
        item-key="name"
        class="dragArea list-group"
      >
        <template #item="{ element }">
          <v-list-item
            :class="['file-item', node.data.selected ? 'selected' : '']"
            :style="{
              paddingInline: '0px !important',
              borderLeft: '1px solid #ccc',
              height: node.data.selected ? '20px' : '16px',
            }"
            @click="clickNode(node)"
            @mouseenter="(evt) => mouseenterNode(evt, node)"
            @mousemove="(evt) => mousemoveNode(evt, node)"
            @mouseleave="(evt) => mouseleaveNode(evt, node)"
            @mousedown="mousedownNode"
            @dragstart="dragstartNode"
            @dragend="dragendNode"
          >
            <template v-slot:prepend>
              <v-spacer class="file-spacer"></v-spacer>
              <v-icon :icon="mdiFile" size="small" density="compact"></v-icon>
            </template>
            <template v-slot:title>
              <span class="node-title">{{ element.name }}</span>
            </template>
            <template v-slot:append>
              <span v-if="nodesSortBy == 'score'" class="node-subtitle">
                ({{ node.data[nodesSortBy] ? formatNumber(node.data[nodesSortBy], 3) : "..." }})
              </span>
              <span v-else-if="nodesSortBy !== 'name'" class="node-subtitle"> ({{ node.data[nodesSortBy] }}) </span>
            </template>
          </v-list-item>
        </template>
      </draggable>
    </template>
  </v-list>
</template>

<script>
import * as d3 from "d3";
import draggable from "vuedraggable";
import { flatten, highlightText, removeExtraNewlines, formatNumber } from "@/utils";
import { mdiChevronRight, mdiChevronDown, mdiFile, mdiFolder } from "@mdi/js";

export default {
  name: "node-list",
  props: ["nodes", "color", "nodesSortBy", "searchTerms", "searchTermPatternMatch", "entity", "updateNodeSelections"],
  components: {
    draggable,
  },
  data: () => {
    return {
      d3: d3,
      flatten: flatten,
      highlightText: highlightText,
      removeExtraNewlines: removeExtraNewlines,
      formatNumber: formatNumber,
      mdiChevronRight: mdiChevronRight,
      mdiChevronDown: mdiChevronDown,
      mdiFile: mdiFile,
      mdiFolder: mdiFolder,
      dragging: false,
    };
  },
  computed: {
    nodesList() {
      return d3.sort(this.nodes, (d) => {
        if (d.data == null) {
          // sort by parent group
          return d.id;
        } else if (this.nodesSortBy == "score") {
          // sort by task score (reverse)
          return -d.data.score;
        } else if (this.nodesSortBy == "name") {
          // sort by txt file name - all txt files are numbered, need to convert to number to sort properly
          return +d.data.name.replace(".txt", "");
        } else {
          return d.data[this.nodesSortBy];
        }
      });
    },
  },
  methods: {
    getNodeColor(node) {
      return this.color(this.getNodeName(node));
    },
    getNodeName(node) {
      return node.id.split("/").at(-1);
    },
    getDirectoryNumFilesMessage(node) {
      if (node.height > 1) {
        return `(${node.children.filter((d) => d.height == 0).length} / ${node.leaves().length})`;
      } else {
        return `(${node.children.length})`;
      }
    },
    getDirectoryBorder(node) {
      return node.depth > 1 ? "1px solid #ccc" : "none";
    },
    someNodesSelected(node) {
      return this.flatten(node)
        .filter((node) => node.data !== null)
        .some((node) => node.data.selected);
    },
    selectAllNodes(node) {
      const allNestedNodes = this.flatten(node).filter((node) => node.data !== null);
      const everyNodeSelected = allNestedNodes.every((node) => node.data.selected);
      const newNodeSelections = allNestedNodes.map((node) => {
        return { id: node.data.id, select: !everyNodeSelected };
      });
      this.updateNodeSelections(newNodeSelections);
    },
    mouseenterNode(event, node) {
      if (!this.dragging) {
        d3.select(".tooltip").style("display", "block").style("opacity", 1).html(this.getTooltipHTML(node.data.text));
      }
    },
    mousemoveNode(event, node) {
      if (!this.dragging) {
        this.positionTooltip(event.x, event.y);
      }
    },
    mouseleaveNode(event, node) {
      if (!this.dragging) {
        d3.select(".tooltip").style("display", "none").style("opacity", 0).html("");
      }
    },
    clickNode(node) {
      this.dragging = false;
      this.updateNodeSelections([{ id: node.data.id, select: !node.data.selected }]);
    },
    mousedownNode() {
      this.dragging = true;
      d3.select(".tooltip").style("display", "none").style("opacity", 0).html("");
    },
    dragstartNode() {
      this.dragging = true;
      d3.select(".tooltip").style("display", "none").style("opacity", 0).html("");
    },
    dragendNode() {
      this.dragging = false;
    },
    /**
     * Positions tooltip near mouse without letting it leave the viewport
     */
    positionTooltip(eventX, eventY) {
      const topPad = 12; // draw tooltip px up from top edge of cursor
      const leftPad = -24; // draw tooltip px left from left edge of cursor
      const tooltip = d3.select(".tooltip");
      const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
      const width = tooltip.node().getBoundingClientRect().width + 2;
      const height = tooltip.node().getBoundingClientRect().height + 2;
      let left = window.scrollX + eventX - leftPad;
      if (left >= vw - width) left = eventX - width + leftPad; // too far right
      let top = window.scrollY + eventY - height - topPad;
      if (top <= 0) top = 0; // too far up
      // if (top <= 0) top = eventY + topPad; // too far up
      tooltip.style("left", `${left}px`).style("top", `${top}px`);
    },
    getTooltipHTML(text) {
      const clean = removeExtraNewlines(text);
      const terms = [
        ...this.searchTerms.map((term) => {
          return { text: term, termClassName: "search-term", patternType: this.searchTermPatternMatch };
        }),
      ];
      if (this.entity.name !== null) {
        terms.push({ text: this.entity.name, termClassName: "entity-term", patternType: "whole-word" });
      }
      const html = this.highlightText(clean, terms);
      return html;
    },
  },
};
</script>

<style lang="scss">
.file-list-container {
  .v-list-item * {
    font-size: 0.8rem !important;
  }

  .v-list-item {
    min-height: 0 !important;
    padding: 0px !important;
    padding-inline-start: 0px !important;
  }

  .v-list-item__spacer {
    width: 2px !important; // space between list item prepend and content
  }

  .directory-numfiles-message {
    opacity: 50%;
    text-align: end;
  }

  .parent-node.selected {
    border-radius: 4px;
    background-color: rgba(255, 255, 255, 0.1) !important;

    .title {
      font-weight: 900;
    }
  }

  .file-item {
    cursor: move;
    // border: 1px solid #048a81;
    // border-radius: 4px;

    .file-spacer {
      width: 6px;
    }

    .file-spacer:before {
      content: "";
      position: absolute;
      top: 50%;
      left: 0;
      border-top: 1px solid #ccc;
      width: 6px;
      transform: translateY(-50%);
    }

    .node-subtitle {
      max-width: 150px;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      opacity: 0.5;
    }
  }

  .file-item.selected {
    border: 1px solid #048a81;
    border-radius: 4px;
    background-color: rgba(255, 255, 255, 0.1);

    .node-title {
      font-weight: 900;
    }
  }

  .file-item:active {
    cursor: grabbing;
  }
}
</style>
