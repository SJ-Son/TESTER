from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        print("Navigating to localhost:5173...")
        page.goto("http://localhost:5173")
        page.wait_for_load_state("networkidle")
        print("Page loaded.")

        # Check if we can access vue app
        is_vue_app = page.evaluate("() => !!document.querySelector('#app').__vue_app__")
        print(f"Vue app detected: {is_vue_app}")

        if not is_vue_app:
            print("Vue app instance not found on #app. Trying to wait...")
            page.wait_for_timeout(2000)
            is_vue_app = page.evaluate("() => !!document.querySelector('#app').__vue_app__")
            print(f"Vue app detected after wait: {is_vue_app}")

        if is_vue_app:
            # Inject generated code to show TestResult
            print("Injecting state...")
            page.evaluate("""() => {
                const app = document.querySelector('#app').__vue_app__;
                // Assuming Pinia is installed
                // Pinia state might be deep in the structure
                // But usually app.config.globalProperties.$pinia is available
                // Or try to find the store.
                // In dev mode, we can try to find the store instance.
                // Or just set the state if we can access the store.

                // Let's try to access the store directly if exposed
                // But usually it's not exposed globally.
                // However, with __vue_app__, we can access the pinia instance.

                const pinia = app.config.globalProperties.$pinia;
                if (pinia) {
                   const testerStore = pinia.state.value.tester;
                   if (testerStore) {
                       testerStore.generatedCode = "def test_example(): pass";
                       testerStore.selectedLanguage = "python";
                   }
                }
            }""")
            print("State injected.")

            # Wait for TestResult to appear
            # The text "Generated Quality Test Suite" is in the header of TestResult
            try:
                page.wait_for_selector("text=Generated Quality Test Suite", timeout=5000)
                print("TestResult component appeared.")
            except:
                print("TestResult component did NOT appear.")
                page.screenshot(path="verification/failed_to_appear.png")

            # Check accessibility attributes
            # Run button
            run_btn = page.locator("button[aria-label='Run test suite']")
            if run_btn.count() > 0:
                print("SUCCESS: Run button found with aria-label")
            else:
                print("FAILURE: Run button NOT found or missing aria-label")

            # Copy button
            copy_btn = page.locator("button[aria-label='Copy code to clipboard']")
            if copy_btn.count() > 0:
                print("SUCCESS: Copy button found with aria-label")
            else:
                print("FAILURE: Copy button NOT found or missing aria-label")

            # Trigger execution to show output console
            # We can just check the buttons first.

            # Now trigger the output console.
            # Clicking Run button will call executeTest.
            if run_btn.count() > 0:
                print("Clicking Run button...")
                run_btn.click()

                # Wait for console to appear
                # It might appear quickly then disappear if error happens?
                # Or executionResult error will show up.
                # "Execution Output" text is in the header of the console
                try:
                    page.wait_for_selector("text=Execution Output", timeout=5000)
                    print("Execution console appeared.")

                    # Check Close button
                    close_btn = page.locator("button[aria-label='Close output panel']")
                    if close_btn.count() > 0:
                        print("SUCCESS: Close button found with aria-label")
                        # Verify it contains SVG (X icon)
                        if close_btn.locator("svg").count() > 0:
                             print("SUCCESS: Close button contains SVG icon")
                        else:
                             print("FAILURE: Close button does NOT contain SVG icon")
                    else:
                        print("FAILURE: Close button NOT found or missing aria-label")

                except Exception as e:
                    print(f"Execution console did not appear: {e}")

        # Take screenshot
        page.screenshot(path="verification/ux_verification.png")
        print("Screenshot saved to verification/ux_verification.png")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path="verification/error.png")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
