import React, { Component } from 'react';
import * as RB from 'react-bootstrap';

class Index extends Component {

  render() {
    const { updateSearchTerm, updateSearchType, requestSearch, searchTerm, searchType } = this.props;

    const BUTTONS = ['Default']; // can add more buttons of various style

    function onSelectAlert(value) {
      updateSearchType(value);
    }


    function renderDropdownButton(title, i) {
      return (
        <RB.DropdownButton
          bsStyle={title.toLowerCase()}
          title={'Type'}
          key={i}
          id={`dropdown-basic-${i}`}>
          <RB.MenuItem eventKey="Mesh"
            onSelect={onSelectAlert}>
              MeSH</RB.MenuItem>
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
                </RB.FormGroup>
                <RB.Button onClick={() => requestSearch(searchTerm, searchType)}>Submit</RB.Button>
              </form>
            </RB.Col>
            <RB.Col xs={4} md={2} />
          </RB.Row>
        </RB.Grid>
      </div>
    )
  }
}

export default Index;