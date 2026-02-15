console.log("LOADED");

const isTrainer = USER_TYPE === 'trainer';
let gridApi = null;
let currentSheet = null;

let isPainting = false;
let paintColor = null;

let isShiftDown = false;

/* =========================
   ✅ MOBILE DETECTION
========================= */
const isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
let isLongPress = false;
let longPressTimer = null;

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
      singleClickEdit: true, // ✅ important for mobile keyboard
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
      singleClickEdit: true, // ✅ mobile editing fix
    },

    rowData: [],

    /* =========================
       CELL VALUE CHANGE
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
       CELL CLICK
    ========================= */
    onCellClicked(params) {

      const paintingMode = isShiftDown || isLongPress;

      // 📱 Mobile tap = edit
      if (!paintingMode) {
        if (isMobile) {
          params.api.startEditingCell({
            rowIndex: params.node.rowIndex,
            colKey: params.column.getColId()
          });
        }
        return;
      }

      // 🎨 Paint logic
      const field = params.colDef.field;
      const colorField = field + '_color';

      const currentColor = params.data[colorField];
      const newColor = currentColor ? '' : '#3bff65';

      params.data[colorField] = newColor;

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

      isPainting = true;
      paintColor = newColor;
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
    },

    onFirstDataRendered: () => {
      if (isMobile) {
        setTimeout(() => {
          document.querySelectorAll(".ag-cell").forEach(cell => {
            cell.style.touchAction = "manipulation";
          });
        }, 200);
      }
    },

  };

  new agGrid.Grid(gridDiv, gridOptions);
  gridApi = gridOptions.api;

  currentSheet = Object.keys(SHEETS)[0];
  gridApi.setRowData(JSON.parse(JSON.stringify(SHEETS[currentSheet])));

  /* =========================
     MOBILE LONG PRESS
  ========================= */
  if (isMobile) {
    function attachTouchToCells() {
      document.querySelectorAll(".ag-cell").forEach(cell => {

        cell.addEventListener("touchstart", function (e) {

          longPressTimer = setTimeout(() => {
            isLongPress = true;
            isPainting = true;

            // simulate click when long press activates
            const rowIndex = cell.getAttribute("row-index");
            const colId = cell.getAttribute("col-id");

            if (rowIndex != null && colId) {
              const rowNode = gridApi.getDisplayedRowAtIndex(Number(rowIndex));
              if (!rowNode) return;

              const colorField = colId + "_color";
              const currentColor = rowNode.data[colorField];
              const newColor = currentColor ? '' : '#3bff65';

              rowNode.data[colorField] = newColor;
              paintColor = newColor;

              gridApi.refreshCells({
                rowNodes: [rowNode],
                columns: [colId],
                force: true
              });
            }

          }, 500); // 500ms long press
        });

        cell.addEventListener("touchend", function () {
          clearTimeout(longPressTimer);
          setTimeout(() => {
            isLongPress = false;
            isPainting = false;
          }, 50);
        });

      });
    }

    // Attach once grid is ready
    setTimeout(attachTouchToCells, 500);
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
