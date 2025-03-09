function printReport() {
    var printContents = document.getElementById("printableReport").innerHTML;
    var originalContents = document.body.innerHTML;

document.body.innerHTML = "<html><head><title>Print Report</title>" +
    "<style>" +
        "body { font-family: Arial, sans-serif; margin: 0; padding: 10px; }" +
        "table { width: auto; max-width: 100%; border-collapse: collapse; table-layout: auto; }" +
        "th, td { border: 1px solid black; text-align: center; padding: 4px; font-size: 12px; word-wrap: break-word; }" +
        "th { background-color: #f2f2f2; }" +
        "@media print {" +
        "  body { margin: 0; padding: 10px; }" + /* Ensures proper print margins */
        "  table { width: 100%; }" + /* Forces table to fit page */
        "  th, td { font-size: 10px; padding: 3px; }" + /* Smaller font for print */
        "}" +
        "</style></head><body>" +
        printContents + "</body></html>";    
        window.print();
        document.body.innerHTML = originalContents;
        location.reload();
        }