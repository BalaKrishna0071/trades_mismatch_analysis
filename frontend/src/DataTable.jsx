import React, { useEffect, useState } from "react";
import axios from "axios";
import "./DataTable.css";

import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";

function DataTable() {
  const [data, setData] = useState([]);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");

  const columns = [
    "Symbol","Strike","Type","Expiry","DC_BUYPRICE","BUYPRICE_API219",
    "BUYPRICE_API135","DC_SELLPRICE","SELLPRICE_API219","SELLPRICE_API135",
    "LTP_NEST","LTP_API219","LTP_API135"
  ];

  const numericColumns = [
    "DC_BUYPRICE","BUYPRICE_API219","BUYPRICE_API135",
    "DC_SELLPRICE","SELLPRICE_API219","SELLPRICE_API135",
    "LTP_NEST","LTP_API219","LTP_API135"
  ];

  const formatNumber = (val) =>
    typeof val === "number" && !isNaN(val) ? val.toFixed(2) : val;

  const fetchData = () => {
    axios
      .get("http://127.0.0.1:5007/get_mismatch_result")
      .then((res) => {
        if (res.status === 200) { // Only update if status is 200
          setData(res.data.data);
          setLastRefresh(new Date());
        } else {
          console.warn("API returned non-200 status:", res.status);
        }
      })
      .catch((err) => console.error("Error fetching data:", err));
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 sec
    return () => clearInterval(interval);
  }, []);

  const query = searchQuery.toLowerCase();

  const filteredData = data.filter((row) =>
    columns.some((col) =>
      row[col]?.toString().toLowerCase().includes(query)
    )
  );

  return (
    <div className="data-table-wrapper">

      <div className="refresh-time">
        {lastRefresh
          ? `Last refreshed: ${lastRefresh.toLocaleString()}`
          : "Loading..."}
      </div>

      <div className="search-wrapper">
        <input
          type="text"
          placeholder="Search......"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>

      <TableContainer component={Paper} className="table-container">
        <Table size="small">

          <TableHead className="table-header">
            <TableRow>
              {columns.map((col) => (
                <TableCell key={col}>{col}</TableCell>
              ))}
            </TableRow>
          </TableHead>

          <TableBody>
            {filteredData.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  align="center"
                  style={{ color: "#888", padding: "20px" }}
                >
                  {searchQuery
                    ? `🔎 No results found for "${searchQuery}"`
                    : "📭 No data available from API"}
                </TableCell>
              </TableRow>
            ) : (
              filteredData.map((row, idx) => (
                <TableRow key={idx} className="table-row">
                  {columns.map((col) => (
                    <TableCell key={col} className="table-cell">
                      {row[col] !== undefined
                        ? numericColumns.includes(col)
                          ? formatNumber(row[col])
                          : row[col]
                        : "-"}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>

        </Table>
      </TableContainer>
    </div>
  );
}

export default DataTable;