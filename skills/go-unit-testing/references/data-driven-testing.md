# Data-Driven Test Template (JSON)

```go
import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"github.com/google/go-cmp/cmp"
)

// testCase represents a single test case loaded from JSON.
type testCase struct {
	Name string `json:"name"`
	In   struct {
		Input <input_type> `json:"input"`
	} `json:"in"`
	Want struct {
		Expected <output_type> `json:"expected"`
	} `json:"want"`
}

// testData represents the JSON test data structure.
type testData struct {
	Tests []testCase `json:"tests"`
}

func Test<FunctionName>DataDriven(t *testing.T) {
	t.Parallel()

	// Load test data from JSON file
	testdataPath := filepath.Join("testdata", "<function>_test.json")
	data, err := os.ReadFile(testdataPath)
	if err != nil {
		t.Fatalf("failed to read test data: %v", err)
	}

	var td testData
	if err := json.Unmarshal(data, &td); err != nil {
		t.Fatalf("failed to parse test data: %v", err)
	}

	for _, tc := range td.Tests {
		t.Run(tc.Name, func(t *testing.T) {
			// Arrange
			input := tc.In.Input
			expected := tc.Want.Expected

			// Act
			got, err := <Function>(input)

			// Assert
			if err != nil {
				t.Errorf("<Function>() unexpected error: %v", err)
			}
			if !cmp.Equal(got, expected) {
				t.Errorf("<Function>(%v) = %v, want %v", input, got, expected)
			}
		})
	}
}
```

- `tests/data/<function>_test.json`
  > JSON file containing test cases.

  ```json
  {
    "tests": [
      {
        "name": "case-description-1",
        "in": {
          "input": <value>
        },
        "want": {
          "expected": <value>
        }
      },
      {
        "name": "case-description-2",
        "in": {
          "input": <value>
        },
        "want": {
          "expected": <value>
        }
      }
    ]
  }
  ```

