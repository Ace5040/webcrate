#!/bin/perl

use strict;
use warnings;
use feature qw(say);
#use List::Util qw(sum sum0 reduce);
use Data::Dumper;

my (@keys, @top);
my @ps = `top -w 512 -b -n 1 | tail -n +8`;
my @data;

for (@ps) {
    my @fields = split /( )* /,$_,4;
    my @row = @fields[0, 2, 4];
    push @data, \@row;
}

my %projects;

for my $row (@data) {

    my @ud = @{$row};
    my $name = $ud[0];

    if ( !exists $projects{$name} ) {
	     $projects{$name}=$row;
    } else {
	    $projects{$name}[1]+=$ud[1];
	    $projects{$name}[2]+=$ud[2];
    }

}

while ( my ($u, $d) = each %projects) {
  printf "stats_projects,user=%s pcpu=%.1f,mem=%di\n", @{$d};
}
