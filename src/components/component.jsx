import React, { Component } from 'react';
import * as RB from 'react-bootstrap';
import ZoomableBurst from './zoomableBurst';
import { Modal } from 'react-bootstrap';



class Index extends Component {
  constructor(props, context) {
    super(props, context);

    this.clickHandler = this.clickHandler.bind(this);
    this.hideModal = this.hideModal.bind(this);

    this.state = {
      activeModal: null,
    };


  }

  clickHandler(e, index) {
    this.setState({ activeModal: index })
  }

  hideModal() {
      this.setState({ activeModal: null })
  }

  render() {
    const { updateSearchTerm, updateSearchType, requestSearch, searchTerm, searchType, results } = this.props;

    const BUTTONS = ['Default']; // can add more buttons of various style

    function onSelectAlert(value) {
      updateSearchType(value);
    }

    function renderDropdownButton(title, i) {
      return (
        <RB.DropdownButton
          bsStyle={title.toLowerCase()}
          title={searchType}
          key={i}
          id={`dropdown-basic-${i}`}>
          <RB.MenuItem eventKey="Mesh"
            onSelect={onSelectAlert}>
              MesH</RB.MenuItem>
          <RB.MenuItem eventKey="Author"
            onSelect={onSelectAlert}>
              Author</RB.MenuItem>
          <RB.MenuItem eventKey="Title"
            onSelect={onSelectAlert}>
              Title</RB.MenuItem>
          <RB.MenuItem divider />
          <RB.MenuItem eventKey="General Keyword"
            onSelect={onSelectAlert}>
            General Keyword
          </RB.MenuItem>
        </RB.DropdownButton>
      );
    }

    const typeButton = (
      <RB.ButtonToolbar>
        {BUTTONS.map(renderDropdownButton)}
      </RB.ButtonToolbar>
    );

    const searchResultComponent = (results ?  
      <div>
      <h4>
        Results:
      </h4>
      <table>
        <tbody>
        <tr>
          <td>Name</td>
          <td>id</td>
          <td>roles</td>
        </tr>
          {results['authors'].map((item, key) => {
            return (
              <tr key = {key}>
              <td>{item.name}</td>
              <td>{item.id}</td>
              <td>{item.roles}</td>
              <td><RB.Button onClick={e => this.clickHandler(e, key)}>
                  View Recs
                </RB.Button></td>
              <Modal id={key} show={this.state.activeModal === key} onHide={this.hideModal}>
                <Modal.Header closeButton>
                  <Modal.Title>Recommendations for {item.name}</Modal.Title>
                </Modal.Header>
                <Modal.Body>{item.name}</Modal.Body>
                <Modal.Footer>
                  <RB.Button onClick={this.hideModal}>
                    Close
                  </RB.Button>
                  <RB.Button  onClick={this.hideModal}>
                    Save Changes
                  </RB.Button>
                </Modal.Footer>
              </Modal>
            </tr>
            )
          })}
        </tbody>
      </table></div> : <h1>no results</h1>);


    return (
      <div>
        <RB.Grid>
          <RB.Row>
            <RB.Col xs={4} md={2} />
            <RB.Col xs={12} md={8}>
              <RB.PageHeader>
                SCOSY - Top Secret Medical Project
                <br />
                <small>
                  by Santiago Buenahora, Garrett Darley, Kunal Garg, Nick Keenan
                </small>
              </RB.PageHeader>
              <form>
                <RB.FormGroup controlId='search'>
                  <RB.Grid>
                    <RB.Row className ="show-grid">
                      <RB.ControlLabel>Please enter a search term</RB.ControlLabel>
                    </RB.Row>
                    <RB.Row className ="show-grid">
                      <RB.Col xs={12} md={6}>
                        <RB.FormControl
                          value={searchTerm}
                          onChange={e => updateSearchTerm(e.target.value)}
                        />
                      </RB.Col>
                      <RB.Col xs={6} md={4}>
                        {typeButton}
                      </RB.Col>
                    </RB.Row>
                  </RB.Grid>
                  <RB.HelpBlock>This search term will be used for finding researcher data</RB.HelpBlock>
                  <RB.Grid>
                  </RB.Grid>
                </RB.FormGroup>
                <RB.Button onClick={() => requestSearch(searchTerm, searchType)}>Submit</RB.Button>
                <hr/>
                {results ? searchResultComponent : <svg width={800} height={800}></svg>}  
              </form>
            </RB.Col>
            <RB.Col xs={4} md={2} />
          </RB.Row>
          <ZoomableBurst/>
        </RB.Grid>
      </div>
    )
  }
}

export default Index;
