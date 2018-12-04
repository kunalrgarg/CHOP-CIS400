import React, { Component } from 'react';
import * as RB from 'react-bootstrap';

class Index extends Component {

  render() {
    const {updateSearchTerm, requestSearch, searchTerm } = this.props;
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
                  <RB.ControlLabel>Please enter a search term</RB.ControlLabel>
                  <RB.FormControl
                    value={searchTerm}
                    onChange={e => updateSearchTerm(e.target.value)}
                  />
                  <RB.HelpBlock>This search term will be used for finding researcher data</RB.HelpBlock>
                </RB.FormGroup>
                <RB.Button onClick={() => requestSearch(searchTerm)}>Submit</RB.Button>
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
