console.log("LOADED") 
const isTrainer = USER_TYPE === 'trainer';
let gridApi = null;  
let currentSheet = null; 
let isPainting = false;
let paintColor = false;
let isShiftDown = false;

function columnNameFromIndex(index) { 
  let name = ''; 
  let n = index;
   while (n >= 0) {
     name = String.fromCharCode((n % 26) + 65) + name; n = Math.floor(n / 26) - 1;
     } 
     return name;
    }

const NUM_COLS = 26;
function generateColumnDefs(numCols) {
   const cols = [
     {
      headerName: '',
      valueGetter: params => {
        if (params.data.row_id === 0) return "Name"; return params.data.row_id; 
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
      cellStyle: params => ({ 
        backgroundColor: params.data?.[colName + '_color'] || '' 
      }), 
    }); 
  } 
  return cols; 
} 

document.addEventListener("keydown", e => {
  if (e.key === "Shift") isShiftDown = true;
});

document.addEventListener("keyup", e => {
  if (e.key === "Shift") isShiftDown = false;
});

document.addEventListener("mouseup", () => {
  isPainting = false;
  paintColor = null;
})

document.addEventListener('DOMContentLoaded', () => { 
  const gridDiv = document.getElementById('grid'); 
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'; 
  const socket = new WebSocket(
    `${protocol}://${window.location.host}/ws/sheet/${CLUB_ID}/`,
  ); 
  gridOptions = { 
    getRowId: params => String(params.data.row_id), 
    columnDefs: generateColumnDefs(NUM_COLS), 
    defaultColDef: { resizable: true, editable: true }, 
    rowData: [], 
    
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
    
    onCellClicked(params) { 
      if (!isShiftDown) return;

      const field = params.colDef.field; 
      const colorField = field + '_color'; 
      const currentColor = params.data[colorField]; 
      const newColor = currentColor ? '' : '#ffeb3b'; 

      params.data[colorField] = newColor
      params.api.refreshCells({ 
        rowNodes: [params.node], columns: [field], force: true 
      }); 
      socket.send(JSON.stringify({ 
        type: 'cell_update', 
        group: currentSheet, 
        row: params.data.row_id, 
        col: field, value: params.value ?? "", 
        color: newColor })); 
      
      isPainting = true;
      paintColor = newColor;
    },

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
      })
    }
    }; 
    
    new agGrid.Grid(gridDiv, gridOptions); 
    gridApi = gridOptions.api; 
    console.log("GRI api:", gridApi); 
    currentSheet = Object.keys(SHEETS)[0]; 
    console.log("Default sheet:", currentSheet); 
    gridApi.setRowData(JSON.parse(JSON.stringify(SHEETS[currentSheet])));

    document.querySelectorAll(".sheet-tab").forEach(btn => { 
      btn.addEventListener("click", () => { 
        const sheetName = btn.dataset.sheet; 
        currentSheet = sheetName; 

        console.log("Switching to: ", currentSheet); 

        gridApi.setRowData([])

        const cloned = JSON.parse(JSON.stringify(SHEETS[currentSheet]));

        gridApi.setRowData(cloned); 
      }); 
    }); 
  });