#!/bin/perl

use strict;
use warnings;
use feature qw(say);
#use List::Util qw(sum sum0 reduce);
use Data::Dumper;

my (@keys, @top);
my @ps = `top -b -n 1 | tail -n +8`;
my @data;

for (@ps) {
    my @fields = split /( )* /,;
    #print Dumper(@fields);
    my @row = @fields[4, 18, 12];
    push @data, \@row;
}

my %users;

for my $row (@data) {

    my @ud = @{$row};
    my $name = $ud[0];

    if ( !exists $users{$name} ) {
	     $users{$name}=$row;
    } else {
	    $users{$name}[1]+=$ud[1];
	    $users{$name}[2]+=$ud[2];
    }

}

printf "cpuperuser";
while ( my ($u, $d) = each %users) {
  printf ",user=%s pcpu=%.1f rss=%di", @{$d};
}
printf "\n";
