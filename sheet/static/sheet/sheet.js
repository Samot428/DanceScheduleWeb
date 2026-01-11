const NUM_ROWS = 100; // počet riadkov ako v exceli

function generateEmptyRows(rowCount, colCount) {
  const rows = [];

  for (let r = 0; r < rowCount; r++) {
    const row = { row_id: r };

    for (let c = 0; c < colCount; c++) {
      const colName = columnNameFromIndex(c);
      row[colName] = '';
      row[colName + '_color'] = '';
    }

    rows.push(row);
  }

  return rows;
}


function columnNameFromIndex(index) {
  let name = '';
  let n = index;

  while (n >= 0) {
    name = String.fromCharCode((n % 26) + 65) + name;
    n = Math.floor(n / 26) - 1;
  }
  return name;
}

const NUM_COLS = 26; // začneme po Z

function generateColumnDefs(numCols) {
  const cols = [
    {
      headerName: '',
      valueGetter: params => params.data.row_id + 1,
      width: 60,
      pinned: 'left',
      editable: false
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

    columnDefs: generateColumnDefs(NUM_COLS),

    defaultColDef: {
      resizable: true,
      editable: true
    },

    rowData: rowData,

    onCellValueChanged(params) {
      const colIndex = params.column.getInstanceId() - 1;

      if (colIndex === gridOptions.columnDefs.length - 2) {
        const nextCol = gridOptions.columnDefs.length - 1;
        const newColName = columnNameFromIndex(nextCol);

        gridOptions.api.addColumnDefs([{
          field: newColName,
          headerName: newColName,
          editable: true
        }]);
      }

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

      const field = params.colDef.field;
      const colorField = field + '_color';
      const currentColor = params.data[colorField];

      const newColor = currentColor ? '' : '#ffeb3b';

      const newData = {
        ...params.data,
        [colorField]: newColor
      };

      params.node.setData(newData);

      params.api.refreshCells({
        rowNodes: [params.node],
        columns: [field],
        force: true
      });

      socket.send(JSON.stringify({
        type: 'cell_update',
        row: params.data.row_id,
        col: field,
        value: params.value ?? "",
        color: newColor
      }));
    }

  };

  agGrid.createGrid(gridDiv, gridOptions);
});
