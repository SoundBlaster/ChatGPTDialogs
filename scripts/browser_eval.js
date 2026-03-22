function stringifyResult(value) {
  if (value === null || value === undefined) {
    return "";
  }
  return String(value);
}

function runSafari(jsCode) {
  var safari = Application("Safari");
  safari.includeStandardAdditions = true;

  if (safari.windows.length === 0 && safari.documents.length === 0) {
    throw new Error("Safari has no open window.");
  }

  try {
    return stringifyResult(safari.doJavaScript(jsCode, { in: safari.windows[0].currentTab() }));
  } catch (error1) {
    try {
      return stringifyResult(safari.windows[0].currentTab().doJavaScript(jsCode));
    } catch (error2) {
      try {
        return stringifyResult(safari.documents[0].doJavaScript(jsCode));
      } catch (error3) {
        throw new Error(
          "Safari JavaScript evaluation failed: " +
          error1 + " | " + error2 + " | " + error3
        );
      }
    }
  }
}

function runChromiumLike(browserName, jsCode) {
  var browser = Application(browserName);
  browser.includeStandardAdditions = true;

  if (browser.windows.length === 0) {
    throw new Error(browserName + " has no open window.");
  }

  try {
    return stringifyResult(browser.windows[0].activeTab().execute({ javascript: jsCode }));
  } catch (error1) {
    try {
      return stringifyResult(browser.windows[0].tabs[0].execute({ javascript: jsCode }));
    } catch (error2) {
      throw new Error(
        browserName + " JavaScript evaluation failed: " + error1 + " | " + error2
      );
    }
  }
}

function run(argv) {
  if (argv.length < 2) {
    throw new Error("Usage: browser_eval.js <browser> <javascript>");
  }

  var browserName = argv[0];
  var jsCode = argv[1];

  if (browserName === "Safari") {
    return runSafari(jsCode);
  }

  if (
    browserName === "Google Chrome" ||
    browserName === "Brave Browser" ||
    browserName === "Chromium"
  ) {
    return runChromiumLike(browserName, jsCode);
  }

  throw new Error(
    "Unsupported browser: " +
    browserName +
    ". Supported: Safari, Google Chrome, Brave Browser, Chromium."
  );
}
