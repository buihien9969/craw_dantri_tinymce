<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('violations', function (Blueprint $table) {
            $table->id('violation_id');
            $table->string('type', 20);
            $table->integer('reference_id');
            $table->string('detected_word', 50);
            $table->timestamp('detected_at')->useCurrent();
            $table->foreignId('handled_by')->nullable()->constrained('users', 'user_id');
            $table->enum('status', ['pending', 'resolved'])->default('pending');
            $table->boolean('warning_sent')->default(false);
        });

    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('violations');
    }
};
