<template>
  <v-card title="Embeddings" subtitle="Visualizing dataset relatedness" :prepend-icon="mdiChartScatterPlot">
    <template v-slot:append>
      <v-btn :icon="mdiClose" @click="isActive = false"></v-btn>
    </template>

    <v-card-text>
      <div class="d-flex justify-center" style="gap: 12px">
        <!-- CONTROLS -->
        <div style="flex: 0 0 256px">
          <!-- SOURCE -->
          <v-select
            v-model="selectedSource"
            :items="sources"
            class="mt-4"
            label="Select dataset to view"
            density="comfortable"
            variant="outlined"
            hide-details
          >
          </v-select>

          <!-- DATASET -->
          <v-select
            v-model="selectedDataset"
            :items="datasets"
            class="mt-4"
            label="Select technique to plot"
            density="comfortable"
            variant="outlined"
            hide-details
          >
          </v-select>

          <!-- COLORBY -->
          <v-select
            v-if="selectedSource == 'documents'"
            v-model="selectedColorBy"
            :items="colorByAttrs"
            class="mt-4"
            label="Select category to color by"
            density="comfortable"
            variant="outlined"
            clearable
            hide-details
          >
          </v-select>

          <!-- NODE -->
          <v-autocomplete
            v-model="selectedNodes[selectedSource]"
            :items="nodes"
            :item-title="nodeLabelAttr"
            :label="'Select ' + selectedSource + ' to highlight'"
            class="mt-4"
            density="comfortable"
            variant="outlined"
            multiple
            clearable
            chips
            closable-chips
            hide-details
            return-object
          >
            <template v-slot:chip="{ item, index, props }">
              <template v-if="index < 1">
                <v-chip v-bind="props" :text="item.title"></v-chip>
              </template>
              <template v-if="index === 1">
                <span class="text-grey text-caption align-self-center">
                  (+{{ selectedNodes[selectedSource].length - 1 }})
                </span>
              </template>
            </template>
          </v-autocomplete>

          <!-- RESET -->
          <v-btn class="mt-4" block @click="resetPlot">Reset Plot</v-btn>
        </div>

        <!-- CHART -->
        <div style="height: 500px; width: 500px">
          <svg ref="embeddingVis"></svg>
        </div>
      </div>
    </v-card-text>
  </v-card>

  <!-- TOOLTIP -->
  <div class="kg-dialog-tooltip"></div>
</template>

<script setup>
import { ref, inject, onMounted, watch } from "vue";
import * as d3 from "d3";
import { scheme20 } from "@/utils";
import { mdiChartScatterPlot, mdiClose } from "@mdi/js";

import vast_documents_umap from "@/assets/data/vast/documents_umap.json";
import vast_documents_tsne from "@/assets/data/vast/documents_tsne.json";
import vast_documents_pca from "@/assets/data/vast/documents_pca.json";
import vast_nodes_umap from "@/assets/data/vast/nodes_umap.json";
import vast_nodes_tsne from "@/assets/data/vast/nodes_tsne.json";
import vast_nodes_pca from "@/assets/data/vast/nodes_pca.json";

// get providers
const { documents } = inject("documents");
const { knowledgeGraph } = inject("knowledgeGraph");

// get props
const props = defineProps(["isActive"]);

// set refs
const embeddingVis = ref(null);
const svgEl = ref(null);
const svgZoom = ref(null);
const svgTransform = ref(null);

const sources = ref([
  { title: "Documents", value: "documents" },
  { title: "Nodes", value: "nodes" },
]);
const datasets = ref([
  { title: "UMAP", value: "umap" },
  { title: "t-SNE", value: "tsne" },
  { title: "PCA", value: "pca" },
]);
const colorByAttrs = ref([
  { title: "Source", value: "source" },
  { title: "Location", value: "location" },
  { title: "Topic", value: "topic" },
  { title: "Cluster", value: "cluster" },
  { title: "Length", value: "text_length" },
]);
const nodes = ref([]); // node data
const nodeData = ref({}); // node data look up
const nodeLabelAttr = ref(""); // attr for node label

const selectedSource = ref("documents"); // which embedding source to look at
const selectedDataset = ref("umap"); // which dataset to visualize
const selectedColorBy = ref(null); // which attribute to color nodes by
const selectedNodes = ref({}); // which nodes to highlight

selectedNodes.value = Object.fromEntries(sources.value.map((x) => [x.value, []])); // set selected nodes per source
setNodes(); // set node list, look-up table, and label attribute

const isActive = props.isActive;

// only plot after inserting elements into DOM
onMounted(() => {
  setTimeout(() => {
    [svgEl.value, svgZoom.value] = plot(embeddingVis.value);
  }, 500);
});

// set watchers
watch(selectedSource, () => {
  setNodes(); // set new nodes
  [svgEl.value, svgZoom.value] = plot(embeddingVis.value); // re-draw plot
});
watch(
  [selectedColorBy, selectedDataset, () => selectedNodes.value[selectedSource.value]],
  () => {
    [svgEl.value, svgZoom.value] = plot(embeddingVis.value); // re-draw plot
  },
  { deep: true }
);

/**
 * Get nodes depending on the source selected.
 */
function setNodes() {
  // set nodes
  if (selectedSource.value == "documents") nodes.value = documents.value;
  if (selectedSource.value == "nodes") nodes.value = knowledgeGraph.value.nodes;
  // set nodes data table
  nodeData.value = Object.fromEntries(
    nodes.value.map((d) => {
      return [d.id, d];
    })
  );
  // set node label attribution
  if (selectedSource.value == "documents") nodeLabelAttr.value = "name";
  if (selectedSource.value == "nodes") nodeLabelAttr.value = "id";
}

/**
 * Draws scatterplot
 *
 * See:
 * - <https://observablehq.com/@d3/scatterplot/2>
 * - <https://observablehq.com/@d3/pan-zoom-axes>
 */
function plot(el) {
  const svg = d3.select(el);
  let width = el.getBoundingClientRect().width;
  let height = el.getBoundingClientRect().height;

  svg.selectAll("*").remove();

  // Specify the chart’s dimensions.
  const marginTop = 24;
  const marginRight = 16;
  const marginBottom = 36;
  const marginLeft = 36;

  // get data
  let data = [];
  if (selectedSource.value == "documents" && selectedDataset.value == "umap") data = vast_documents_umap;
  if (selectedSource.value == "documents" && selectedDataset.value == "tsne") data = vast_documents_tsne;
  if (selectedSource.value == "documents" && selectedDataset.value == "pca") data = vast_documents_pca;
  if (selectedSource.value == "nodes" && selectedDataset.value == "umap") data = vast_nodes_umap;
  if (selectedSource.value == "nodes" && selectedDataset.value == "tsne") data = vast_nodes_tsne;
  if (selectedSource.value == "nodes" && selectedDataset.value == "pca") data = vast_nodes_pca;

  // get color scale
  let color;
  if (selectedSource.value == "documents" && selectedColorBy.value) {
    // assign selected color by values to each data point
    const attrs = Object.fromEntries(nodes.value.map((doc) => [doc.id, doc[selectedColorBy.value]]));
    data.forEach((document) => (document[selectedColorBy.value] = attrs[document.id]));

    // construct color scale
    if (selectedColorBy.value == "text_length") {
      // continous, sequential color scale
      color = d3.scaleSequential(
        d3.extent(data, (d) => d[selectedColorBy.value]),
        d3.interpolateViridis
      );
    } else {
      // discrete, categorical color scale
      const groups = Array.from(new Set(data.map((d) => d[selectedColorBy.value])));
      if (groups.length <= 20) {
        // <20 groups, use categorical scale
        color = d3.scaleOrdinal(groups, scheme20);
      } else {
        // 21+ groups, chop up continuous scale
        color = (group) => d3.interpolateTurbo(groups.indexOf(group) / groups.length);
      }
    }
  }

  // Prepare the scales for positional encoding.
  const x = d3
    .scaleLinear()
    .domain(d3.extent(data, (d) => d.x))
    .nice()
    .range([marginLeft, width - marginRight]);

  const y = d3
    .scaleLinear()
    .domain(d3.extent(data, (d) => d.y))
    .nice()
    .range([height - marginBottom, marginTop]);

  // Create the axes.
  const xAxis = d3.axisBottom(x).ticks(width / 80);
  const gX = svg
    .append("g")
    .attr("transform", `translate(0,${height - marginBottom})`)
    .call(xAxis)
    .call((g) => g.select(".domain").remove());

  const yAxis = d3.axisLeft(y);
  const gY = svg
    .append("g")
    .attr("transform", `translate(${marginLeft},0)`)
    .call(yAxis)
    .call((g) => g.select(".domain").remove());

  // create view
  const view = svg.append("g");

  // Create the grid.
  view
    .append("g")
    .attr("stroke", "currentColor")
    .attr("stroke-opacity", 0.1)
    .call((g) =>
      g
        .append("g")
        .selectAll("line")
        .data(x.ticks())
        .join("line")
        .attr("x1", (d) => 0.5 + x(d))
        .attr("x2", (d) => 0.5 + x(d))
        .attr("y1", marginTop)
        .attr("y2", height - marginBottom)
    )
    .call((g) =>
      g
        .append("g")
        .selectAll("line")
        .data(y.ticks())
        .join("line")
        .attr("y1", (d) => 0.5 + y(d))
        .attr("y2", (d) => 0.5 + y(d))
        .attr("x1", marginLeft)
        .attr("x2", width - marginRight)
    );

  // Add a layer of dots.
  const circles = view
    .append("g")
    .selectAll("circle")
    .data(data)
    .join("circle")
    .attr("stroke", (d) => (nodeIsSelected(d.id) ? "#EE8434" : color ? color(d[selectedColorBy.value]) : "steelblue"))
    .attr("stroke-width", 1.5)
    .attr("stroke-opacity", (d) => (nodeIsSelected(d.id) ? 1 : 0.35))
    .attr("fill", (d) => (nodeIsSelected(d.id) ? "#EE8434" : color ? color(d[selectedColorBy.value]) : "steelblue"))
    .attr("fill-opacity", (d) => (nodeIsSelected(d.id) ? 1 : 0.15))
    .attr("r", (d) => (nodeIsSelected(d.id) ? 4 : 4))
    .attr("cx", (d) => x(d.x))
    .attr("cy", (d) => y(d.y));

  // bring selected node to the front
  circles
    .filter((d) => nodeIsSelected(d.id))
    .each(function () {
      d3.select(this).raise();
    });

  // Add a layer of labels.
  const labels = view
    .append("g")
    .attr("font-family", "sans-serif")
    .attr("paint-order", "stroke")
    .attr("stroke", "white")
    .selectAll("text")
    .data(data)
    .join("text")
    .attr("display", (d) => (nodeIsSelected(d.id) ? "block" : "none"))
    .attr("dy", "0.35em")
    .attr("font-size", 10)
    .attr("stroke-width", 3)
    .attr("x", (d) => x(d.x) + 12)
    .attr("y", (d) => y(d.y))
    .text((d) => nodeData.value[d.id][nodeLabelAttr.value]);

  // add interactions to circles
  circles
    .on("mouseenter", function (evt, d) {
      const el = d3.select(this);
      el.raise(); // bring node to the front
      labels
        .filter((l) => l.id == d.id && !nodeIsSelected(d.id))
        .each(function () {
          d3.select(this).attr("display", "block"); // show label
        });
    })
    .on("mouseleave", function (evt, d) {
      labels
        .filter((l) => l.id == d.id && !nodeIsSelected(d.id))
        .each(function () {
          d3.select(this).attr("display", "none"); // hide label
        });
    })
    .on("click", (evt, d) => {
      svgTransform.value = d3.zoomTransform(view.node()); // save transform
      selectNode(d.id);
    });

  // get zoom function
  const zoom = d3
    .zoom()
    .scaleExtent([0.5, 80])
    .translateExtent([
      [-100, -100],
      [width + 90, height + 100],
    ])
    .filter(filter)
    .on("zoom", zoomed);

  // apply zoom function
  svg.call(zoom);

  // re-apply zoom
  if (svgTransform.value !== null) svg.call(zoom.transform, svgTransform.value);

  return [svg, zoom];

  /**
   * Apply zoom transformation
   */
  function zoomed({ transform }) {
    view.attr("transform", transform);
    gX.call(xAxis.scale(transform.rescaleX(x)));
    gY.call(yAxis.scale(transform.rescaleY(y)));
    const scaleFactor = transform.k;
    labels.attr("x", (d) => x(d.x) + 12 / scaleFactor);
    labels.attr("font-size", 10 / scaleFactor);
    labels.attr("letter-spacing", 1 / scaleFactor);
    labels.attr("stroke-width", 3 / scaleFactor);
    circles.attr("stroke-width", 1.5 / scaleFactor);
    circles.attr("r", (d) => (nodeIsSelected(d.id) ? 4 / scaleFactor : 4 / scaleFactor));
    svgTransform.value = d3.zoomTransform(view.node()); // save transform
  }

  /**
   * prevent scrolling then apply the default filter
   */
  function filter(event) {
    event.preventDefault();
    return (!event.ctrlKey || event.type === "wheel") && !event.button;
  }
}

/**
 * Reset zoom.
 */
function resetPlot() {
  svgEl.value.transition().duration(750).call(svgZoom.value.transform, d3.zoomIdentity);
}

/**
 * Add node to selected list, if not already exists.
 */
function selectNode(nodeId) {
  if (!nodeIsSelected(nodeId)) selectedNodes.value[selectedSource.value].push(nodeData.value[nodeId]);
}

/**
 * Returns whether node with id is selected.
 */
function nodeIsSelected(nodeId) {
  return selectedNodes.value[selectedSource.value].some((node) => node.id == nodeId);
}
</script>

<style lang="scss"></style>
