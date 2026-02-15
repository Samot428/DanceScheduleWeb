console.log("LOADED");

const isTrainer = USER_TYPE === 'trainer';
let gridApi = null;
let currentSheet = null;

let isPainting = false;
let paintColor = null;
let isShiftDown = false;

/* =========================
   MOBILE DETECTION
========================= */
const isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
let paintMode = false; // mobile toggle mode

/* =========================
   COLUMN NAME HELPER
========================= */
function columnNameFromIndex(index) {
  let name = '';
  let n = index;
  while (n >= 0) {
    name = String.fromCharCode((n % 26) + 65) + name;
    n = Math.floor(n / 26) - 1;
  }
  return name;
}

const NUM_COLS = 26;

/* =========================
   COLUMN DEFINITIONS
========================= */
function generateColumnDefs(numCols) {

  const cols = [
    {
      headerName: '',
      valueGetter: params => {
        if (params.data.row_id === 0) return "Name";
        return params.data.row_id;
      },
      width: 80,
      pinned: 'left',
      editable: false,
      cellStyle: { textAlign: 'center', fontWeight: 'bold' }
    },
    {
      headerName: "Day",
      field: "day",
      width: 120,
      pinned: "left",
      editable: isTrainer,
      cellClass: 'readonly-cell',
      cellRenderer: params => params.value || "",
    },
    {
      headerName: 'Time',
      field: 'time',
      width: 100,
      pinned: 'left',
      editable: isTrainer,
      cellClass: 'readonly-cell',
      cellRenderer: params => params.value || "",
    }
  ];

  for (let i = 0; i < numCols; i++) {
    const colName = columnNameFromIndex(i);

    cols.push({
      field: colName,
      headerName: colName,
      editable: true,
      singleClickEdit: true, // mobile keyboard support
      cellStyle: params => ({
        backgroundColor: params.data?.[colName + '_color'] || ''
      }),
    });
  }

  return cols;
}

/* =========================
   DESKTOP SHIFT HANDLING
========================= */
document.addEventListener("keydown", e => {
  if (e.key === "Shift") isShiftDown = true;
});

document.addEventListener("keyup", e => {
  if (e.key === "Shift") isShiftDown = false;
});

document.addEventListener("mouseup", () => {
  isPainting = false;
  paintColor = null;
});

/* =========================
   MAIN
========================= */
document.addEventListener('DOMContentLoaded', () => {

  const gridDiv = document.getElementById('grid');

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const socket = new WebSocket(
    `${protocol}://${window.location.host}/ws/sheet/${CLUB_ID}/`,
  );

  const gridOptions = {

    getRowId: params => String(params.data.row_id),

    columnDefs: generateColumnDefs(NUM_COLS),

    defaultColDef: {
      resizable: true,
      editable: true,
      singleClickEdit: true,
    },

    rowData: [],

    /* =========================
       SEND UPDATE
    ========================= */
    onCellValueChanged(params) {
      socket.send(JSON.stringify({
        type: 'cell_update',
        group: currentSheet,
        row: params.data.row_id,
        col: params.colDef.field,
        value: params.newValue ?? "",
        color: params.data[params.colDef.field + '_color'] ?? ""
      }));
    },

    /* =========================
       CLICK BEHAVIOR
    ========================= */
    onCellClicked(params) {

      const paintingMode = isShiftDown || paintMode;

      // 📱 Mobile tap when NOT in paint mode → edit
      if (!paintingMode) {
        if (isMobile) {
          params.api.startEditingCell({
            rowIndex: params.node.rowIndex,
            colKey: params.column.getColId()
          });
        }
        return;
      }

      // 🎨 PAINT
      const field = params.colDef.field;
      const colorField = field + '_color';

      const currentColor = params.data[colorField];
      const newColor = currentColor ? '' : '#3bff65';

      params.data[colorField] = newColor;
      paintColor = newColor;
      isPainting = true;

      params.api.refreshCells({
        rowNodes: [params.node],
        columns: [field],
        force: true
      });

      socket.send(JSON.stringify({
        type: 'cell_update',
        group: currentSheet,
        row: params.data.row_id,
        col: field,
        value: params.value ?? "",
        color: newColor
      }));
    },

    /* =========================
       DESKTOP DRAG PAINT
    ========================= */
    onCellMouseOver(params) {

      if (!isPainting || !isShiftDown) return;

      const field = params.colDef.field;
      const colorField = field + '_color';

      if (params.data[colorField] === paintColor) return;

      params.data[colorField] = paintColor;

      params.api.refreshCells({
        rowNodes: [params.node],
        columns: [field],
        force: true,
      });

      socket.send(JSON.stringify({
        type: 'cell_update',
        group: currentSheet,
        row: params.data.row_id,
        col: field,
        value: params.value ?? "",
        color: paintColor
      }));
    }
  };

  new agGrid.Grid(gridDiv, gridOptions);
  gridApi = gridOptions.api;

  currentSheet = Object.keys(SHEETS)[0];
  gridApi.setRowData(JSON.parse(JSON.stringify(SHEETS[currentSheet])));

  /* =========================
     MOBILE PAINT BUTTON
  ========================= */
  if (isMobile) {

    const paintBtn = document.createElement("button");
    paintBtn.innerText = "🎨 Paint";
    paintBtn.style.position = "fixed";
    paintBtn.style.bottom = "20px";
    paintBtn.style.right = "20px";
    paintBtn.style.zIndex = "9999";
    paintBtn.style.padding = "12px 18px";
    paintBtn.style.borderRadius = "12px";
    paintBtn.style.border = "none";
    paintBtn.style.background = "#3bff65";
    paintBtn.style.fontWeight = "bold";
    paintBtn.style.boxShadow = "0 4px 12px rgba(0,0,0,0.2)";

    document.body.appendChild(paintBtn);

    paintBtn.addEventListener("click", () => {
      paintMode = !paintMode;
      isPainting = false;

      paintBtn.style.background = paintMode ? "#ff3b3b" : "#3bff65";
      paintBtn.innerText = paintMode ? "❌ Stop" : "🎨 Paint";
    });
  }

  /* =========================
     SHEET SWITCHING
  ========================= */
  document.querySelectorAll(".sheet-tab").forEach(btn => {
    btn.addEventListener("click", () => {

      const sheetName = btn.dataset.sheet;
      currentSheet = sheetName;

      gridApi.setRowData([]);

      const cloned = JSON.parse(JSON.stringify(SHEETS[currentSheet]));
      gridApi.setRowData(cloned);
    });
  });

});
