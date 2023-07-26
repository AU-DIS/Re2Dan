import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"

interface State {
  isFocused: boolean
}

/**
 * This is a React-based component template. The `render()` function is called
 * automatically when your component should be re-rendered.
 */
class MyComponent extends StreamlitComponentBase<State> {
  public state = { isFocused: false }

  public render = (): ReactNode => {
    // Arguments that are passed to the plugin in Python are accessible
    // via `this.props.args`. Here, we access the "name" arg.
    const words = this.props.args["words"]

    var patient_words = words.map(function (word: string[]) {

      if (word.length === 1) {
        return <text> {word[0]} </text>
      }
      else {
        return <> <button
          style={{ border: "none", backgroundColor: word[1] }}
          key={word[0]}
          onClick={() => Streamlit.setComponentValue(word[0])}
        >
          {word[0]}
        </button> <text> </text> </>
      }
    })
    return <> {patient_words}  </>

  }

}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
export default withStreamlitConnection(MyComponent)
