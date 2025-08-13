async function fetchInvoiceDetails() {
    const response = await fetch('http://localhost:8000/invoice/');
    const data = await response.json();
    document.getElementById('date').textContent = data.date_issued;
    document.getElementById('invoiceNo').textContent = data.invoice_number;
    updateTable(data.table_data);
}

async function addRow() {
    const description = document.getElementById('description').value;
    const quantity = parseInt(document.getElementById('quantity').value);
    const price = parseFloat(document.getElementById('price').value);

    if (description && quantity > 0 && price >= 0) {
        const response = await fetch('http://localhost:8000/invoice/add_row', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description, quantity, price })
        });
        const data = await response.json();
        updateTable(data.table_data);
        document.getElementById('description').value = '';
        document.getElementById('quantity').value = '';
        document.getElementById('price').value = '';
    } else {
        alert('Please fill all fields correctly.');
    }
}

function updateTable(data) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';
    let grandTotal = 0;
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.no}</td>
            <td>${row.description}</td>
            <td>${row.quantity}</td>
            <td>₹${row.price.toFixed(2)}</td>
            <td>₹${row.subtotal.toFixed(2)}</td>
        `;
        tbody.appendChild(tr);
        grandTotal += row.subtotal;
    });
    document.getElementById('grandTotal').textContent = grandTotal.toFixed(2);
}

async function generatePDFContent() {
    // Fetch CSS content
    const cssResponse = await fetch('styles.css');
    const cssContent = await cssResponse.text();
    
    // Capture the invoice details and table content, excluding buttons
    const invoiceDetails = document.querySelector('.invoice-details').outerHTML;
    const tableContainer = document.querySelector('.table-container').cloneNode(true);
    const pdfButton = tableContainer.querySelector('.pdf-button');
    const telegramButton = tableContainer.querySelector('.telegram-button');
    if (pdfButton) pdfButton.remove();
    if (telegramButton) telegramButton.remove();
    
    // Create HTML content for PDF with embedded CSS
    return `
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                ${cssContent}
                body { font-family: Arial, sans-serif; margin: 20px; }
                .pdf-button, .telegram-button { display: none; }
            </style>
        </head>
        <body>
            <h1>Invoice</h1>
            ${invoiceDetails}
            ${tableContainer.outerHTML}
        </body>
        </html>
    `;
}

async function downloadPDF() {
    const htmlContent = await generatePDFContent();
    
    // Send HTML content to backend for PDF generation
    const response = await fetch('http://localhost:8000/invoice/generate_pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ html: htmlContent })
    });
    
    if (!response.ok) {
        throw new Error(`PDF generation failed: ${response.statusText}`);
    }
    
    // Trigger download
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = response.headers.get('content-disposition')?.split('filename=')[1] || 'invoice.pdf';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

async function sendToTelegram() {
    const htmlContent = await generatePDFContent();
    
    // Send HTML content to backend for Telegram
    const response = await fetch('http://localhost:8000/invoice/send_to_telegram', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ html: htmlContent })
    });
    
    if (!response.ok) {
        throw new Error(`Failed to send PDF to Telegram: ${response.statusText}`);
    }
    
    const data = await response.json();
    alert(data.message);
}

// Fetch invoice details on page load
fetchInvoiceDetails();