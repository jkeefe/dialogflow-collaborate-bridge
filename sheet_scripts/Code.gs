function onOpen() {

    // this code runs when the spreadsheet is opened
    var ui = SpreadsheetApp.getUi();
    ui.createMenu('Update')
        .addItem('Update All Sheets','updateSheets')
        .addToUi();
      
}

function updateSheets() {

    // Hit the lambda function to trigger update of the latest data
    var response = UrlFetchApp.fetch("https://r2drvfpno4.execute-api.us-east-1.amazonaws.com/prod/updatesheets");

    var text_returned = response.getContentText();
  
    var ui = SpreadsheetApp.getUi();
    var result = ui.alert(
        'Dialogflow/Collaborate bridge responded:',
        text_returned,
        ui.ButtonSet.OK);
}
