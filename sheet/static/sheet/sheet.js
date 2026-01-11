const NUM_ROWS = 20; // počet riadkov ako v exceli

function generateEmptyRows(count) {
  const rows = [];
  for (let i = 0; i < count; i++) {
    rows.push({
      row_id: i,
      a: '',
      b: '',
      a_color: '',
      b_color: ''
    });
  }
  return rows;
}

document.addEventListener('DOMContentLoaded', () => {
  const gridDiv = document.getElementById('grid');
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';

  // const socket = new WebSocket(`${protocol}://${window.location.host}/ws/sheet/`);
  const socket = new WebSocket(
    `${protocol}://${window.location.host}/ws/sheet/${CLUB_ID}/`
  );


  const rowData = (typeof initialData !== 'undefined' && initialData.length > 0)
    ? initialData
    : generateEmptyRows(NUM_ROWS);

  const gridOptions = {
    getRowId: params => params.data.row_id,

    columnDefs: [
      {
        headerName: '',
        valueGetter: params => params.data.row_id + 1,
        width: 60,
        pinned: 'left',
        editable: false
      },
      {
        field: 'a',
        headerName: 'A',
        cellStyle: params => {
          return params.data?.a_color ? { backgroundColor: params.data.a_color } : null;
        }
      },
      {
        field: 'b',
        headerName: 'B',
        cellStyle: params => {
          return params.data?.b_color ? { backgroundColor: params.data.b_color } : null;
        }
      }
    ],

    defaultColDef: {
      resizable: true,
      editable: true
    },

    rowData: rowData,

    onCellValueChanged(params) {
      socket.send(JSON.stringify({
        type: 'cell_update',
        row: params.data.row_id,
        col: params.colDef.field,
        value: params.newValue ?? "",
        color: params.data[params.colDef.field + '_color'] ?? ""
      }));
    },

    onCellClicked(params) {
      if (!params.event.shiftKey) return;

      const color = '#ffeb3b';
      const colorField = params.colDef.field + '_color';

      // 1️⃣ Update the data
      const newData = { ...params.data, [colorField]: color };
      params.node.setData(newData); // <-- important: use setData to trigger refresh

      // 2️⃣ Force refresh the cell styles
      params.api.refreshCells({
        rowNodes: [params.node],
        columns: [params.colDef.field],
        force: true
      });

      // 3️⃣ Send updated color to backend
      socket.send(JSON.stringify({
        type: 'cell_update',
        row: params.data.row_id,
        col: params.colDef.field,
        value: params.value ?? "",
        color: color
      }));
    }
  };

  agGrid.createGrid(gridDiv, gridOptions);
});
